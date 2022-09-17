import json
import threading
from typing import Dict, Callable, Any
import pika
from pika.exceptions import StreamLostError

from pycti.connector.new.libs.connector_utils import get_logger

# from pycti.connector.new.libs.opencti_schema import ConnectorMessage
from pycti.connector.new.libs.opencti_schema import WorkerMessage
from pycti.connector.new.libs.orchestrator_schemas import RunContainer


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
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error!!! {str(e)}")
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
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, worker_message: WorkerMessage, routing_key: str):
        self.logger.info(f"Sending container: {worker_message.json()}")
        print(f"Sending container: {worker_message.json()}")


    def stop(self):
        pass
