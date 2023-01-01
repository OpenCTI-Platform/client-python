import json
from typing import Callable, Dict

import pika
from pika.exceptions import NackError, StreamLostError, UnroutableError

from pycti.connector.libs.connector_utils import get_logger
from pycti.connector.libs.opencti_schema import WorkerMessage


class PikaBroker(object):
    def __init__(self, broker_settings: Dict) -> None:
        self.callback_function = None
        self.logger = get_logger("PikaBroker", "INFO")
        self.broker_settings = broker_settings
        pika_credentials = pika.PlainCredentials(
            broker_settings["connection"]["user"], broker_settings["connection"]["pass"]
        )

        self.channel = None

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=broker_settings["connection"]["host"],
                port=broker_settings["connection"]["port"],
                virtual_host="/",
                credentials=pika_credentials,
            )
        )

    def listen_stream(self, queue: str, callback_function: Callable):
        pass

    def listen(self, queue: str, callback_function: Callable, qos_limit: int = 1):
        self.channel = self.connection.channel()
        self.callback_function = callback_function

        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=qos_limit)
        self.channel.basic_consume(
            queue=queue, on_message_callback=self.callback, auto_ack=True
        )
        try:
            self.channel.start_consuming()
        except StreamLostError:
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
            self.logger.error(f"Connector run error: {str(e)}")
            return

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, worker_message: WorkerMessage, routing_key: str):
        channel = self.connection.channel()
        try:
            channel.basic_publish(
                exchange=self.broker_settings["push_exchange"],
                routing_key=routing_key,
                body=json.dumps(worker_message.json()).encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        except (UnroutableError, NackError) as e:
            self.logger.error("Unable to send bundle, retry...%s", e)
            self.send(worker_message, routing_key)

    def send_test(self, worker_message: WorkerMessage, exchange: str):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type="fanout")
        try:
            channel.basic_publish(
                exchange=exchange,
                routing_key="",
                body=json.dumps(worker_message.json()).encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        except (UnroutableError, NackError, StreamLostError) as e:
            self.logger.error("Unable to send bundle, retry...%s", e)
            self.send_test(worker_message, exchange)

    def stop(self):
        if self.channel:
            try:
                self.channel.stop_consuming()
                # self.channel.close()
            except (StreamLostError, AttributeError):
                # No idea why pika throws this exception when closing
                pass
        elif self.connection:
            try:
                self.connection.close()
            except (StreamLostError, AttributeError):
                # No idea why pika throws this exception when closing
                pass
