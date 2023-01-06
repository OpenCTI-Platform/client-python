import base64
import json
import signal
import threading
import time
from datetime import datetime
from typing import Callable, Dict, List

import schedule
from pydantic import ValidationError
from stix2 import Bundle

from pycti import OpenCTIApiClient, OpenCTIStix2Splitter
from pycti.connector.connector_types.connector_settings import ConnectorBaseConfig
from pycti.connector.libs.connector_utils import get_logger
from pycti.connector.libs.messaging.pika_broker import PikaBroker
from pycti.connector.libs.messaging.stdout_broker import StdoutBroker
from pycti.connector.libs.opencti_schema import WorkerMessage

BROKERS = {"pika": PikaBroker, "stdout": StdoutBroker}
HEARTBEAT_INTERVAL = 40


class Connector(object):
    connector_type = None
    scope = None
    # Settings = configuration for the connector execution
    settings: ConnectorBaseConfig = ConnectorBaseConfig
    # Config = configuration for the opencti connector job
    config: Callable = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)

        if self.scope:
            self.base_config = self.settings(
                type=self.connector_type, connector_scope=self.scope
            )
        else:
            self.base_config = self.settings(type=self.connector_type)

        self.logger = get_logger("Connector", self.base_config.log_level)

        # This will be removed once the job configs are being retrieved during
        # job execution
        if self.config == "":
            self.logger.error("Please define the connector config!")
            return
        elif self.config is not None:
            self.connector_config = self.config()

        self.api = OpenCTIApiClient(
            self.base_config.url,
            self.base_config.token,
            self.base_config.log_level,
            json_logging=self.base_config.json_logging,
        )
        self.splitter = OpenCTIStix2Splitter()

        configuration = self.register_connector(self.base_config.id)

        self.connector_state = {}
        self.applicant_id = configuration["connector_user_id"]
        connector_state = configuration["connector_state"]
        self.set_state(connector_state)
        self.broker_config = configuration["config"]

        self.heartbeat = None
        if not self.base_config.run_and_terminate:
            self.heartbeat = Heartbeat(
                self.api,
                self.base_config.id,
                self.base_config.log_level,
                HEARTBEAT_INTERVAL,
                self.set_state,
                self.get_state,
            )
            self.heartbeat.start()

        try:
            self.broker = self.initiate_broker(
                self.base_config.broker, self.broker_config
            )
        except Exception as e:
            self.logger.error(f"Broker initiation error: {e}")
            self.stop()
            return

        self.broker_thread = None
        self.work_id = None

        self.init()
        self.logger.info("Connector set up")

    def init(self) -> None:
        pass

    def start(self) -> None:
        pass

    def register_connector(self, connector_id: str) -> dict:
        connector_configuration = self.api.connector.register(self)
        self.logger.info(f"Connector registered with ID: {connector_id}")
        return connector_configuration

    def _send_bundle(
        self,
        bundle: Bundle,
        work_id: str,
        applicant_id: str = None,
        entity_types: List = None,
    ):
        # Bundle splitting isn't helping during test runs
        if not self.base_config.testing:
            try:
                sending_bundles = self.splitter.split_bundle(
                    bundle.serialize(), True, None
                )
            except Exception as e:
                self.logger.error(f"Parsing error: {str(e)}")
                raise ValueError(e)
        else:
            sending_bundles = [bundle.serialize()]

        if entity_types is None:
            entity_types = []
        elif isinstance(entity_types, str):
            entity_types = entity_types.split(",")

        if len(sending_bundles) == 0:
            self.logger.info("Nothing to import")
            return

        self.api.work.add_expectations(work_id, len(sending_bundles))

        for sequence, bundle in enumerate(sending_bundles, start=1):
            try:
                worker_message = WorkerMessage(
                    work_id=work_id,
                    applicant_id=applicant_id,
                    action_sequence=sequence,
                    entities_types=entity_types,
                    update=True,
                    content=base64.b64encode(bundle.encode("utf-8")).decode("utf-8"),
                )
            except ValidationError as e:
                self.logger.error(f"Worker Message validation error {e}")
                continue

            if self.base_config.testing:
                queue = f"{self.base_config.name.lower()}-ex"
                self.broker.send_test(worker_message, queue)
            else:
                routing_key = f"push_routing_{self.base_config.id}"
                self.broker.send(worker_message, routing_key)

    def _stop(self):
        pass

    def stop(self, *args) -> None:
        self.logger.info("Shutting down. Please hold the line...")

        if self.heartbeat:
            self.heartbeat.stop()
            self.heartbeat.join()

        self._stop()

        if self.broker:
            self.broker.stop()
        if self.broker_thread:
            self.broker_thread.join()
        self.logger.info("Good bye")

    def set_state(self, state: Dict) -> None:
        """sets the connector state

        :param state: state object
        :type state: Dict
        """
        if state is None:
            self.connector_state = {}
        else:
            self.connector_state |= state

    def get_state(self) -> Dict:
        """get the connector state

        :return: returns the current state of the connector if there is any
        :rtype:
        """
        return self.connector_state

    def get_last_run(self) -> None:
        keys = self.connector_state.keys()
        for key in keys:
            if key == "last_run":
                continue
            del self.connector_state[key]

        current_state = self.get_state()
        last_run = current_state.get("last_run", None)
        if last_run:
            self.logger.info(
                "Connector last run: "
                + datetime.utcfromtimestamp(last_run).strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            self.logger.info("Connector has never run")

    def set_last_run(self) -> None:
        timestamp = int(time.time())
        self.set_state({"last_run": timestamp})

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

    @staticmethod
    def initiate_broker(broker: str, broker_config: Dict):
        broker_class = BROKERS.get(broker, None)
        if broker_class is None:
            raise NotImplementedError(f"Invalid broker '{broker}'")

        try:
            broker_object = broker_class(broker_config)
        except Exception as e:
            raise AssertionError(f"Broker could not be launched: {e}")

        return broker_object


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
        except ValueError as e:
            self.logger.error(f"Killing didn't go as planned ({e})")

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
        except Exception as e:
            self.in_error = True
            self.logger.error(f"Error pinging the API '{e}'")
