import base64
import json
import schedule
import signal
import socket
import threading
import traceback
from typing import Optional, Dict, Callable, Union, List

import requests
import time
from pydantic import Json, BaseModel, BaseSettings
from stix2 import Bundle
from stix2.workbench import parse

from pycti import OpenCTIApiClient, OpenCTIStix2Splitter
from pycti.connector.new.connector_types.connector_settings import ConnectorBaseConfig
from pycti.connector.new.libs.messaging.stdout_broker import StdoutBroker
from pycti.connector.new.libs.connector_utils import get_logger
from pycti.connector.new.libs.messaging.pika_broker import PikaBroker
from pycti.connector.new.libs.opencti_schema import WorkerMessage


class Connector(object):
    # object for the connector specific config
    connector_type = None
    config: Callable = None
    scope: str = None
    settings: ConnectorBaseConfig = ConnectorBaseConfig

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)

        self.base_config = self.settings(type=self.connector_type, scope=self.scope)
        self.logger = get_logger("Connector", self.base_config.log_level)
        if self.config == "":
            self.logger.error("Please define the connector config!")
            return
        if self.config is not None:
            self.connector_config = self.config()

        self.api = OpenCTIApiClient(
            self.base_config.url,
            self.base_config.token,
            self.base_config.log_level,
            json_logging=self.base_config.json_logging,
        )
        self.splitter = OpenCTIStix2Splitter()

        configuration = self.register_connector(self.base_config.id)

        self.work_id = None
        self.applicant_id = configuration["connector_user"]["id"]
        connector_state = configuration["connector_state"]
        self.set_state(connector_state)
        self.broker_config = configuration["config"]

        if not self.base_config.run_and_terminate:
            self.heartbeat = Heartbeat(
                self.api,
                self.base_config.id,
                self.base_config.log_level,
                40,
                self.set_state,
                self.get_state,
            )
            self.heartbeat.start()

        if self.base_config.broker == "pika":
            try:
                self.broker = PikaBroker(self.broker_config)
            except socket.gaierror as e:
                self.logger.error(
                    f"Unable to contact broker: {self.broker_config['connection']['host']}:{self.broker_config['connection']['port']} -> {str(e)}"
                )
                return
        elif self.base_config.broker == "stdout":
            self.broker = StdoutBroker(self.broker_config)
        else:
            self.logger.error(f"Invalid broker {self.base_config.broker}!")
            return

        self.broker_thread = None
        self.stdout_broker = None

        if self.base_config.testing:
            self.stdout_broker = StdoutBroker(self.broker_config)

        self.logger.info("Connector set up")

    def start(self) -> None:
        pass

    def register_connector(self, connector_id: str) -> dict:
        connector_configuration = self.api.connector.register(self)
        self.logger.info("%s", f"Connector registered with ID: {connector_id}")
        return connector_configuration

    def _send_bundle(self, bundle: Bundle, work_id: str, applicant_id: str = None, entity_types: List = None):
        sending_bundles = []
        if not self.base_config.testing:
            try:
                sending_bundles = self.splitter.split_bundle(bundle.serialize(), True, None)
            except Exception as e:
                self.logger.error(f"Parsing error: {str(e)}")
        else:
            sending_bundles = [bundle.serialize()]

        if entity_types is None:
            entity_types = []

        if len(sending_bundles) == 0:
            self.logger.error("Nothing to import")
            return

        self.api.work.add_expectations(work_id, len(sending_bundles))
        routing_key = f"push_routing_{self.base_config.id}"

        for sequence, bundle in enumerate(sending_bundles, start=1):
            worker_message = WorkerMessage(work_id=work_id,
                                           applicant_id=applicant_id,
                                           action_sequence=sequence,
                                           entities_types=entity_types,
                                           update=True,
                                           content=base64.b64encode(bundle.encode("utf-8")).decode("utf-8")
                                           )
            self.logger.info(f"Sending off {bundle}")

            if self.base_config.testing:
                self.logger.info(f"Routing to stdout")
                self.stdout_broker.send(worker_message, routing_key)
            else:
                self.broker.send(worker_message, routing_key)

    def _stop(self):
        pass

    def stop(self, *args) -> None:
        self.logger.info("Shutting down. Please hold the line...")
        if not self.base_config.run_and_terminate:
            self.heartbeat.stop()
            self.heartbeat.join()
        self._stop()
        if self.broker_thread:
            self.broker.stop()
            self.broker_thread.join()

    def set_state(self, state) -> None:
        """sets the connector state

        :param state: state object
        :type state: Dict
        """
        self.connector_state = json.dumps(state)

    def get_state(self) -> Optional[Dict]:
        """get the connector state

        :return: returns the current state of the connector if there is any
        :rtype:
        """

        try:
            if self.connector_state:
                state = json.loads(self.connector_state)
                if isinstance(state, Dict) and state:
                    return state
        except:  # pylint: disable=bare-except  # noqa: E722
            pass
        return None

    def to_input(self) -> Dict:
        return self.to_dict()

    def to_dict(self) -> Dict:
        """connector input to use in API query

        :return: dict with connector data
        :rtype: dict
        """
        return {
            "input": {
                "id": self.base_config.id,
                "name": self.base_config.name,
                "type": self.base_config.type,
                "scope": self.base_config.scope,
                "auto": self.base_config.auto,
                "only_contextual": self.base_config.contextual_only,
            }
        }


class Heartbeat(threading.Thread):
    def __init__(
            self,
            api: OpenCTIApiClient,
            connector_instance: str,
            log_level: str,
            interval: int,
            set_state: Callable,
            get_state: Callable,
    ):
        threading.Thread.__init__(self)
        self.api = api
        self.connector_instance = connector_instance
        # self.connector_id = connector_id
        self.interval = interval
        self.logger = get_logger("ConnectorHeartbeat", log_level)
        self.set_state = set_state
        self.get_state = get_state
        self.in_error = False

        self.event = schedule.every(self.interval).seconds.do(self.run_heartbeat)
        self.logger.info("Starting ping alive thread")
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        try:
            self.logger.info("Preparing for clean shutdown")
            self.stop_event.set()
            # time.sleep(2)
            # self.s.cancel(self.event)
            # schedule.clear()
        except ValueError as e:
            self.logger.error("Killing didn't go as planned")

    def run_heartbeat(self):
        try:
            initial_state = self.get_state()
            result = self.api.connector.ping(self.connector_instance, initial_state)

            remote_state = result.get("connector_state", None)
            if remote_state is not None:
                remote_state = json.loads(remote_state)

            if initial_state != remote_state:
                self.set_state(remote_state)
                self.logger.info(
                    f"Connector state has been remotely reset to: '{self.get_state()}'"
                )

            if self.in_error:
                self.in_error = False

            self.logger.error("API Ping back to normal")
        except Exception:  # pylint: disable=broad-except
            self.in_error = True
            self.logger.error("Error pinging the API")