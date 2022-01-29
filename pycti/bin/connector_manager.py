import json
import logging
import threading
from typing import Dict, Callable

import pika
from celery import Celery, chain
from celery.canvas import Signature
from apscheduler.schedulers.background import BackgroundScheduler
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel

from pycti import OpenCTIApiClient
from pycti.connector_v2.libs.connector_utils import get_logger, create_ssl_context
from pycti.connector_v2.libs.pika_broker import PikaBroker

RABBITMQ_USER = "SjIHMjmnYyRtuDf"
RABBITMQ_PASS = "EVOCuAGfhOEYmmt"
RABBITMQ_HOST = "rabbitmq"

class ConnectorManager(object):
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.celery_app = Celery(
            backend="redis://redis.ssh.local",
            broker=f"pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//"
        )

        self.logger = get_logger("Connector Manager", 3)
        self.use_ssl = False
        self.port = 5672
        self.opencti_url = "https://opencti.ssh.local"
        self.opencti_token = "18bd74e5-404c-4216-ac74-23de6249d690"
        self.queue_name = "connector_manager_queue"

        self.api = OpenCTIApiClient(
            self.opencti_url,
            self.opencti_token,
            3
        )
        self.listen(self.run)
        self.exit_event = threading.Event()

    def run(self, data: Dict) -> None:
        # tasks
        # register new/updated connector
        # remove connector
        # initiate direct call to connector
        if data['command'] == "add_schedule":
            job = self._prepare_celery_chain()
            self.scheduler.scheduled_job(job)
        elif data['command'] == "run_enrichment":
            job = self._prepare_celery_chain()
            result = job()
            print(result.get())

    def _prepare_celery_chain(self):
        c1 = Signature("c1.connector", queue='c1')
        c2 = Signature("c2.stix_ingester", queue='c2')
        job = chain(c1, c2)
        return job


    def listen(self, callback_function: Callable) -> None:
        while not self.exit_event.is_set():
            try:
                # Connect the broker
                self.pika_connection = self._get_pika_blocking_connection()
                self.channel = self.pika_connection.channel()
                assert self.channel is not None
                # TODO add self.callback_function = callback_function as func arguments instead of global variable!!
                self.callback_function = callback_function
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except Exception as e:
                self.logger.error(str(e), exc_info=True)

    def _data_handler(self, json_data) -> None:
        # Set the API headers
        work_id = json_data["internal"]["work_id"]
        applicant_id = json_data["internal"]["applicant_id"]
        self.work_id = work_id
        if applicant_id is not None:
            self.applicant_id = applicant_id
            self.api.set_applicant_id_header(applicant_id)
        # Execute the callback
        try:
            self.api.work.to_received(
                work_id, "Connector ready to process the operation"
            )
            message = self.callback_function(json_data["event"])
            self.api.work.to_processed(work_id, message)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.exception("Error in message processing, reporting error to API")
            try:
                self.api.work.to_processed(work_id, str(e), True)
            except:  # pylint: disable=bare-except
                self.logger.error("Failing reporting the processing")

    ###  functions for further messaging handling
    def _process_message(
        self,
        channel: BlockingChannel,
        method: spec.Basic.Deliver,
        properties: spec.BasicProperties,
        body: bytes,
    ) -> None:
        """process a message from the rabbit queue

        :param channel: channel instance
        :type channel: callable
        :param method: message methods
        :type method: callable
        :param properties: unused
        :type properties: str
        :param body: message body (data)
        :type body: str or bytes or bytearray
        """

        json_data = json.loads(body)
        self.thread = threading.Thread(target=self._data_handler, args=[json_data])
        self.thread.start()
        while self.thread.is_alive():  # Loop while the thread is processing
            assert self.pika_connection is not None
            self.pika_connection.sleep(1.0)
        self.logger.info(
            f"Message (delivery_tag={method.delivery_tag}) processed, thread terminated"
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _get_pika_blocking_connection(self) -> pika.BlockingConnection:
        pika_credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

        pika_parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=self.port,
            virtual_host="/",
            credentials=pika_credentials,
            ssl_options=pika.SSLOptions(create_ssl_context(), RABBITMQ_HOST)
            if self.use_ssl
            else None,
        )
        return pika.BlockingConnection(pika_parameters)


class PingHandler(threading.Thread):
    def __init__(
        self,
        connector_id: str,
        graphql_connector: ConnectorGraphQLHandler,
        get_state: Callable,
        set_state: Callable,
        logger: logging.Logger,
    ) -> None:
        threading.Thread.__init__(self)
        self.connector_id = connector_id
        self.in_error = False
        self.graphql_connector = graphql_connector
        self.get_state = get_state
        self.set_state = set_state
        self.exit_event = threading.Event()
        self.logger = logger

    def ping(self) -> None:
        while not self.exit_event.is_set():
            try:
                initial_state = self.get_state()
                result = self.graphql_connector.ping(initial_state)
                remote_state = (
                    json.loads(result["connector_state"])
                    if result["connector_state"] and len(result["connector_state"]) > 0
                    else None
                )
                if initial_state != remote_state:
                    self.set_state(result["connector_state"])
                    self.logger.info(
                        "%s",
                        (
                            "Connector state has been remotely reset to: "
                            f'"{self.get_state()}"'
                        ),
                    )
                if self.in_error:
                    self.in_error = False
                    self.logger.error("API Ping back to normal")
            except Exception as e:
                self.in_error = True
                self.logger.error(f"Error pinging the API {e}")
            self.exit_event.wait(40)

    def run(self) -> None:
        self.logger.info("Starting ping alive thread")
        self.ping()

    def stop(self) -> None:
        self.logger.info("Preparing ping for clean shutdown")
        self.exit_event.set()
