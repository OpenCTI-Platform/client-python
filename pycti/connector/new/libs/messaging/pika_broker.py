import json
import socket
import threading
from typing import Dict, Callable
import pika
from pika.exceptions import StreamLostError, NackError, UnroutableError
from stix2 import Bundle

from pycti.connector.new.libs.connector_utils import get_logger
from pycti.connector.new.libs.opencti_schema import WorkerMessage
from pycti.connector.new.libs.orchestrator_schemas import RunContainer


class PikaBroker(object):
    def __init__(self, broker_settings: Dict) -> None:
        # threading.Thread.__init__(self)
        self.callback_function = None
        self.logger = get_logger("PikaBroker", "INFO")
        self.broker_settings = broker_settings
        pika_credentials = pika.PlainCredentials(
            broker_settings["connection"]["user"], broker_settings["connection"]["pass"]
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=broker_settings["connection"]["host"],
                port=broker_settings["connection"]["port"],
                virtual_host="/",
                credentials=pika_credentials,
            )
        )
        self.stop_listen_event = threading.Event()

    def listen_stream(self, queue: str, callback_function: Callable):
        pass

    def listen(self, queue: str, callback_function: Callable):
        self.channel = self.connection.channel()
        self.callback_function = callback_function

        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue, on_message_callback=self.callback, auto_ack=True
        )
        try:
            self.channel.start_consuming()
        except StreamLostError as e:
            # No idea why pika throws this exception when closing
            pass

    def callback(self, ch, method, properties, body):
        self.logger.info(f"Received {body}")

        try:
            msg = json.loads(body)
        except Exception as e:
            self.logger.error(f"Received non-json packet ({body}) -> {e} ")
            return
        # Execute the callback
        try:
            self.callback_function(msg)
        except Exception as e:
            self.logger.error(f"Error!!! {str(e)}")
        # TODO get task
        # for connector:
        #   get task message
        # for stix worker:
        #   get stix bundle and ingest
        # try:
        #     run_container = RunContainer(**json.loads(body.decode()))
        # except Exception as e:
        #     print(f"Received unknown container format {e}")
        #     return
        #     # Print log
        #     # accept delivery?
        #     # send message to orchestrator that it failed? (but for which config?)
        #
        # try:
        #     self.callback_function(run_container)
        # except Exception as e:
        #     # TODO handle exceptions (in case something went wrong)
        #     # then no container is passed and the job as well as the run
        #     # are set to failed result
        #     # do something??...
        #     print(f"errorr: {str(e)}")
        #     return
        # # manual ack is necessary, when rerunning connector
        # or should we only rerun entire workflow runs?
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, worker_message: WorkerMessage, routing_key: str):
        channel = self.connection.channel()
        try:
            channel.basic_publish(
                exchange=self.broker_settings["push_exchange"],
                routing_key=routing_key,
                body=json.dumps(worker_message.json()).encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        except (UnroutableError, NackError) as e:
            self.logger.error("Unable to send bundle, retry...%s", e)
            self.send(worker_message, routing_key)

    def stop(self):
        if self.channel:
            try:
                self.channel.stop_consuming()
                # self.channel.close()
            except StreamLostError as e:
                # No idea why pika throws this exception when closing
                pass
        else:
            self.connection.close()
