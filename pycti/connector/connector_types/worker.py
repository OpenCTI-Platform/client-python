import base64
import functools
import json
import random
import signal
import threading
import time
from threading import Thread
from typing import Any, Dict, List

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import StreamLostError
from requests import RequestException, Timeout

from pycti import ConnectorType, OpenCTIApiClient
from pycti.connector.connector_types.connector_settings import WorkerConfig
from pycti.connector.libs.connector_utils import get_logger
from pycti.connector.libs.opencti_schema import WorkerMessage
from pycti.connector.opencti_connector_helper import create_ssl_context

PROCESSING_COUNT: int = 3
MAX_PROCESSING_COUNT: int = 30
INTERVAL: int = 10


class WorkerConsumer(Thread):
    connector: Dict[str, Any]
    opencti_url: str
    opencti_token: str

    def __init__(
        self, connector, opencti_url, opencti_token, log_level, ssl_verify, json_logging
    ) -> None:
        super().__init__()
        self.connector = connector
        self.opencti_url = opencti_url
        self.opencti_token = opencti_token

        self.logger = get_logger(f"WorkerThread-{self.connector['id']}", log_level)

        self.api = OpenCTIApiClient(
            url=self.opencti_url,
            token=self.opencti_token,
            log_level=log_level,
            ssl_verify=ssl_verify,
            json_logging=json_logging,
        )
        self.queue_name = self.connector["config"]["push"]
        self.pika_credentials = pika.PlainCredentials(
            self.connector["config"]["connection"]["user"],
            self.connector["config"]["connection"]["pass"],
        )
        self.pika_parameters = pika.ConnectionParameters(
            self.connector["config"]["connection"]["host"],
            self.connector["config"]["connection"]["port"],
            "/",
            self.pika_credentials,
            ssl_options=pika.SSLOptions(create_ssl_context())
            if self.connector["config"]["connection"]["use_ssl"]
            else None,
        )

        self.pika_connection = pika.BlockingConnection(self.pika_parameters)
        self.channel = self.pika_connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.processing_count: int = 0
        self.stop_listen_event = threading.Event()

    def callback(
        self,
        channel: BlockingChannel,
        method: Any,
        properties: str,
        body: str,
    ) -> None:
        try:
            self.logger.info(f"Received {body}")
            msg = json.loads(json.loads(body))
        except Exception as e:
            self.logger.error(f"Received non-json packet ({body}) -> {e} ")
            cb = functools.partial(self.nack_message, channel, method.delivery_tag)
            self.pika_connection.add_callback_threadsafe(cb)
            return

        # Execute the callback
        try:
            self.process_message(msg)

            # Ack the message
            cb = functools.partial(self.ack_message, channel, method.delivery_tag)
            self.pika_connection.add_callback_threadsafe(cb)

        except Timeout as te:
            self.logger.warning(f"A connection timeout occurred: {{ {te} }}")
            # Platform is under heavy load: wait for unlock & retry almost indefinitely.
            sleep_jitter = round(random.uniform(10, 30), 2)
            time.sleep(sleep_jitter)
            self.callback(channel, method, properties, body)
        except RequestException as re:
            self.logger.error(f"A connection error occurred: {{ {re} }}")
            time.sleep(INTERVAL)
            self.logger.info(
                f"Message (delivery_tag={method.delivery_tag}) NOT acknowledged"
            )
            cb = functools.partial(self.nack_message, channel, method.delivery_tag)
            self.pika_connection.add_callback_threadsafe(cb)
            self.processing_count = 0
        except Exception as ex:  # pylint: disable=broad-except
            error = str(ex)
            if "LockError" in error and self.processing_count < MAX_PROCESSING_COUNT:
                # Platform is under heavy load:
                # wait for unlock & retry almost indefinitely.
                sleep_jitter = round(random.uniform(10, 30), 2)
                time.sleep(sleep_jitter)
                self.callback(channel, method, properties, body)
            elif (
                "MissingReferenceError" in error
                and self.processing_count < PROCESSING_COUNT
            ):
                # In case of missing reference, wait & retry
                sleep_jitter = round(random.uniform(1, 3), 2)
                time.sleep(sleep_jitter)
                self.logger.info(
                    f"Message (delivery_tag={method.delivery_tag}) reprocess (retry nb: {self.processing_count})"
                )
                self.callback(channel, method, properties, body)
            elif "Bad Gateway" in error:
                self.logger.error(f"A connection error occurred: {{ {error} }}")
                time.sleep(INTERVAL)
                self.logger.info(
                    f"Message (delivery_tag={method.delivery_tag}) NOT acknowledged"
                )
                cb = functools.partial(self.nack_message, channel, method.delivery_tag)
                self.pika_connection.add_callback_threadsafe(cb)
                self.processing_count = 0
            else:
                # Platform does not know what to do and raises an error:
                # fail and acknowledge the message.
                self.logger.error(f"Unknown error: {error}")
                self.processing_count = 0
                cb = functools.partial(self.ack_message, channel, method.delivery_tag)
                self.pika_connection.add_callback_threadsafe(cb)
                if msg.work_id is not None:
                    self.api.work.report_expectation(
                        msg.work_id, {"error": error, "source": body}
                    )

    def process_message(self, message: Dict) -> None:
        try:
            msg = WorkerMessage(**message)
        except Exception as e:
            self.logger.error(f"Received non-WorkerMessage packet ({message}) -> {e} ")
            raise ValueError(f"Received non-WorkerMessage packet ({message}) -> {e} ")

        # Set the API headers
        self.api.set_applicant_id_header(msg.applicant_id)
        # Execute the import
        self.processing_count += 1
        content = "Unparseable"
        content = base64.b64decode(msg.content).decode("utf-8")
        processing_count = self.processing_count
        if self.processing_count == PROCESSING_COUNT:
            processing_count = None  # type: ignore
        self.api.stix2.import_bundle_from_json(
            content, msg.update, msg.entities_types, processing_count
        )
        if msg.work_id is not None:
            self.api.work.report_expectation(msg.work_id, None)
        self.processing_count = 0

    def run(self) -> None:
        try:
            # Consume the queue
            self.logger.info(f"Thread for queue {self.queue_name} started")
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
            )
            try:
                self.channel.start_consuming()
            except StreamLostError:
                # No idea why pika throws this exception when closing
                pass
        except Exception as e:
            self.logger.error(f"Thread for queue {self.queue_name} failed with {e}")
        finally:
            self.channel.stop_consuming()
            self.logger.info(f"Thread for queue {self.queue_name} terminated")

    def nack_message(self, channel: BlockingChannel, delivery_tag: int) -> None:
        if channel.is_open:
            self.logger.info(f"Message (delivery_tag={delivery_tag}) rejected")
            channel.basic_nack(delivery_tag)
        else:
            self.logger.info(
                f"Message (delivery_tag={delivery_tag}) NOT rejected (channel closed)",
            )

    def ack_message(self, channel: BlockingChannel, delivery_tag: int) -> None:
        if channel.is_open:
            self.logger.info(f"Message (delivery_tag={delivery_tag}) acknowledged")
            channel.basic_ack(delivery_tag)
        else:
            self.logger.info(
                f"Message (delivery_tag={delivery_tag}) "
                "NOT acknowledged (channel closed)"
            )

    def stop(self):
        self.logger.info("Requesting shutdown")
        if self.channel:
            try:
                self.channel.stop_consuming()
                # self.channel.close()
            except (StreamLostError, AttributeError):
                # No idea why pika throws this exception when closing
                pass
        else:
            try:
                self.pika_connection.close()
            except StreamLostError:
                # No idea why pika throws this exception when closing
                pass


class Worker(object):
    connector_type = ConnectorType.WORKER.value
    settings = WorkerConfig

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)

        self.base_config = self.settings()
        self.logger = get_logger("Worker", self.base_config.log_level)

        self.api = OpenCTIApiClient(
            self.base_config.url,
            self.base_config.token,
            self.base_config.log_level,
            json_logging=self.base_config.json_logging,
        )

        # No heartbeat for now, since OpenCTI doesn't support
        # heartbeats for workers
        #
        # self.heartbeat = Heartbeat(
        #     self.api,
        #     self.base_config.id,
        #     self.base_config.log_level,
        #     40,
        #     self.set_state,
        #     self.get_state,
        # )
        # self.heartbeat.start()

        # TODO implement dynamic broker handling
        #
        # if self.base_config.broker == "pika":
        #     try:
        #         self.broker = PikaBroker(self.broker_config)
        #     except socket.gaierror as e:
        #         self.logger.error(
        #             f"Unable to contact broker: {self.broker_config['connection']['host']}:{self.broker_config['connection']['port']} -> {str(e)}"
        #         )
        #         return
        # else:
        #     self.logger.error(f"Invalid broker {self.base_config.broker}!")
        #     return

        self.consumer_threads: Dict[str, Any] = {}
        self.logger_threads: Dict[str, Any] = {}

        self.connectors: List[Any] = []
        self.queues: List[Any] = []
        self.stop_event = threading.Event()
        self.start_finished = False

        self.logger.info("Worker set up")

    def start(self) -> None:
        sleep_delay = INTERVAL
        while not self.stop_event.is_set():
            if sleep_delay == 0:
                sleep_delay = 1
            else:
                sleep_delay <<= 1
            sleep_delay = min(INTERVAL, sleep_delay)
            try:
                self.iterate_queues()
                self.clean_queues(sleep_delay)
            except Exception as e:
                self.logger.error(f"Fatal error: {e}")
                time.sleep(INTERVAL)

        self.start_finished = True

    def stop(self, *args) -> None:
        self.logger.info("Shutting down. Please hold the line...")
        self.stop_event.set()
        while not self.start_finished:
            time.sleep(0.1)

        for thread_name in list(self.consumer_threads):
            self.consumer_threads[thread_name].stop()
            self.consumer_threads[thread_name].join()
        self.logger.info("Finished")

    def iterate_queues(self):
        # Fetch queue configuration from API
        self.connectors = self.api.connector.list()
        self.queues = list(
            map(lambda x: x["config"]["push"], self.connectors)  # type: ignore
        )

        # Check if all queues are consumed
        for connector in self.connectors:
            queue = connector["config"]["push"]
            if queue in self.consumer_threads and not self.stop_event.is_set():
                if not self.consumer_threads[queue].is_alive():
                    self.logger.info(
                        f"Thread for queue {queue} not alive, creating a new one..."
                    )
                    self.consumer_threads[queue] = WorkerConsumer(
                        connector,
                        self.base_config.url,
                        self.base_config.token,
                        self.base_config.log_level,
                        self.base_config.ssl_verify,
                        self.base_config.json_logging,
                    )
                    self.consumer_threads[queue].start()
            else:
                self.consumer_threads[queue] = WorkerConsumer(
                    connector,
                    self.base_config.url,
                    self.base_config.token,
                    self.base_config.log_level,
                    self.base_config.ssl_verify,
                    self.base_config.json_logging,
                )
                self.consumer_threads[queue].start()

    def clean_queues(self, sleep_delay: int):
        # Check if some threads must be stopped
        for thread in list(self.consumer_threads):
            if thread not in self.queues and not self.stop_event.is_set():
                self.logger.info(
                    f"Queue {thread} no longer exists, killing thread...",
                )
                try:
                    self.consumer_threads[thread].stop()
                    # self.consumer_threads[thread].terminate()
                    self.consumer_threads.pop(thread, None)
                    sleep_delay = 1
                except Exception as e:
                    self.logger.warning(
                        f"Unable to kill the thread for queue {thread}, an operation is running, keep trying... ({e})"
                    )
        time.sleep(sleep_delay)
