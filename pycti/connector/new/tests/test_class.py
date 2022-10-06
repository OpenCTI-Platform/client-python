import json
import threading
from time import sleep
from typing import Type, Optional, List

from pika.exceptions import StreamLostError
from stix2 import Bundle

from pycti import OpenCTIApiClient, ConnectorType
from pycti.connector.new.connector import Connector

from pika import BlockingConnection, ConnectionParameters, PlainCredentials


class ConnectorTest:
    connector = None

    def __init__(self, api_client: OpenCTIApiClient):
        self.api_client = api_client
        self.connector_instance = None

    def _setup(self, monkeypatch):
        pass

    def setup(self, monkeypatch):
        monkeypatch.setenv("opencti_url", self.api_client.opencti_url)
        monkeypatch.setenv("opencti_token", self.api_client.api_token)
        self._setup(monkeypatch)

    def run(self):
        self.connector_instance = self.connector()
        self.t1 = threading.Thread(target=self.connector_instance.start)
        self.t1.start()

    def teardown(self):
        pass

    # returns work_id if returned
    def initiate(self) -> Optional[str]:
        pass

    def shutdown(self):
        self.connector_instance.stop()
        self.t1.join()
        self.api_client.connector.unregister(self.connector_instance.base_config.id)

    def get_connector(self) -> Type[Connector]:
        pass

    def verify(self, bundle: Bundle):
        pass


class DummyConnector(object):
    def to_input(self):
        return {
            "input": {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "RabbitMQ Credentials Connector",
                "type": ConnectorType.EXTERNAL_IMPORT.value,
                "scope": "",
                "auto": False,
                "only_contextual": False,
            }
        }


class RabbitMQ:
    def __init__(self, host, port, username, password):
        self.messages = []
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def setup(self):
        self.connection = BlockingConnection(
            ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host="/",
                credentials=PlainCredentials(self.username, self.password),
            )
        )
        self.channel = self.connection.channel()

    def run(self, connector_name: str):
        self.exchange = f"{connector_name}-ex"
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="fanout")

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.queue = result.method.queue
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=self._on_message, auto_ack=True
        )

        self.broker_thread = threading.Thread(
            target=self.channel.start_consuming, name="Broker Listen"
        )

        self.broker_thread.daemon = True
        self.broker_thread.start()

    def shutdown(self):
        if self.channel:
            try:
                self.channel.stop_consuming()
                # self.channel = self.connection.channel()
                # self.channel.queue_delete(queue=self.queue)
                # self.channel.exchange_delete(exchange=self.exchange)
                # self.channel.close()
            except StreamLostError as e:
                # No idea why pika throws this exception when closing
                pass
        else:
            try:
                self.connection.close()
            except StreamLostError as e:
                # No idea why pika throws this exception when closing
                pass

        self.broker_thread.join()

    def get_messages(self) -> List[str]:
        cnt = 3
        while cnt > 0:
            if len(self.messages) == 0:
                sleep(3)
                cnt -= 1
                # Maybe the messages haven't arrived yet
            else:
                cnt = 0
        return self.messages

    def _on_message(self, channel, method_frame, header_frame, body):
        try:
            msg = json.loads(body)
            self.messages.append(msg)
        except Exception as e:
            print(f"Unable to parse message {str(e)}")
