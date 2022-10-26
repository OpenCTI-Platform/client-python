import json
from typing import Dict, Callable

from pycti.connector.libs.connector_utils import get_logger

from pycti.connector.libs.opencti_schema import WorkerMessage


class StdoutBroker(object):
    def __init__(self, broker_settings: Dict) -> None:
        self.logger = get_logger("StdoutBroker", "INFO")
        self.callback_function = None
        self.broker_settings = broker_settings

    def listen_stream(self, queue: str, callback_function: Callable):
        pass

    def listen(self, queue: str, callback_function: Callable):
        self.callback_function = callback_function

    def callback(self, body: str):
        try:
            msg = json.loads(body)
        except Exception as e:
            self.logger.error(f"Received non-json packet ({body}) -> {e} ")
            return

        # Execute the callback
        try:
            self.callback_function(msg)
        except Exception as e:
            print(f"Connector run error: {str(e)}")

    def send(self, worker_message: WorkerMessage, routing_key: str):
        self.logger.info(f"Sending container: {worker_message.json()}")
        print(f"Sending container: {worker_message.json()}")

    def stop(self):
        pass
