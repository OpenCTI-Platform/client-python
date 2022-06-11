import json
import sched
import signal
import threading
import traceback

import requests
import time
from pydantic import Json, BaseModel
from stix2 import Bundle
from stix2.workbench import parse

from pycti.connector.v2.connectors.utils import ConnectorBaseConfig, RunException
from pycti.connector.v2.libs.orchestrator_schemas import (
    ConnectorCreate,
    Connector as ConnectorSchema,
    RunContainer,
    State,
    Result,
    Config,
    RunUpdate,
)
from pycti.connector.v2.libs.connector_utils import get_logger
from pycti.connector.v2.libs.pika_broker import PikaBroker


class Connector(object):
    def __init__(self, connector_create: ConnectorCreate):
        signal.signal(signal.SIGINT, self.stop)
        self.connector_config = connector_create.config_schema
        # signal.signal(signal.SIGTERM, self.stop)

        self.base_config = ConnectorBaseConfig()
        (
            self.environment_config,
            self.connector_instance,
            self.connector,
        ) = self.register_connector(connector_create)
        self.logger = get_logger(self.connector.name, self.base_config.log_level)

        self.logger.info(
            f"Registered with base_config {self.environment_config}. Connector instance: {self.connector_instance}"
        )

        if self.environment_config["broker"]["type"] == "pika":
            self.broker = PikaBroker(
                self.environment_config["broker"], self.process_broker_message
            )
            self.broker_thread = threading.Thread(
                target=self.broker.listen,
                name="Pika Broker Listen",
                args=[self.connector.queue],
            )
            self.broker_thread.daemon = True
            self.broker_thread.start()
        else:
            print("Invalid broker. Exiting")

        self.heartbeat = Heartbeat(
            self.base_config.scheduler,
            self.connector_instance,
            self.base_config.log_level,
            self.environment_config["heartbeat"]["interval"],
        )
        self.heartbeat.start()

        # self.api.
        self.logger.info("Started")

    def register_connector(
        self, connector_create: ConnectorCreate
    ) -> (dict, str, ConnectorSchema):
        connector_create.config_schema = connector_create.config_schema.schema_json()
        response = requests.post(
            url=f"{self.base_config.scheduler}/connector/", json=connector_create.dict()
        )
        if response.status_code != 201:
            raise ValueError(
                f"Got response code {response.status_code} '{response.text}'"
            )

        try:
            content = json.loads(response.text)
        except ValueError:
            raise ValueError(f"Got invalid response '{response.text}'")

        connector = ConnectorSchema(**content["connector"])
        return content["environment"], content["connector_instance"], connector

    def process_broker_message(self, run: RunContainer) -> RunContainer:
        # TODO need to introduce two connector classes (Expert, Importer) (ETL?)
        job = run.jobs.pop(0)
        print(f"Received {job}")
        config = self.get_config(job.config_id)

        response_code, response_msg = self.update_status(
            job.config_id, run.run_id, State.running
        )
        if response_code != 200:
            self.update_status(job.config_id, run.run_id, State.finished, Result.fail)
            raise RunException(
                f"Unable to set Connector to running mode for Run {run.run_id}: {response_msg} ({response_code})"
            )

        try:
            my_config = self.connector_config(**config.config)
            if run.bundle is None:
                bundle = run.bundle
            else:
                bundle = parse(run.bundle)
            bundle = self.run(bundle, my_config)
            if isinstance(bundle, Bundle):
                bundle = bundle.serialize()
            run.bundle = bundle
        except ValueError as e:  # pydantic validation error
            raise RunException(f"Unable to parse config {str(e)}")
        except Exception as e:
            raise RunException(f"Run error {str(e)} {traceback.format_exc()}")

        response_code, response_msg = self.update_status(
            job.config_id, run.run_id, State.finished, Result.success
        )
        if response_code != 200:
            self.update_status(job.config_id, run.run_id, State.finished, Result.fail)
            raise RunException(
                f"Unable to set Connector to finished mode for Run {run.run_id}: {response_msg} ({response_code})"
            )

        return run

    def run(self, bundle: Json | str | None, config: BaseModel) -> Bundle:
        pass

    def get_config(self, config_id: str) -> Config:
        response = requests.get(url=f"{self.base_config.scheduler}/config/{config_id}")
        if response.status_code != 200:
            raise ValueError(
                f"Got response code {response.status_code} '{response.text}'"
            )

        try:
            config = Config(**json.loads(response.text))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Unable to parse Config {response.text} ({str(e)}")

        return config

    def update_status(
        self, config_id: str, run_id: str, status: State, result: Result = None
    ) -> (int, str):
        print(f"running update {config_id}")
        update_schema = RunUpdate(
            command="job_status",
            parameters={"config_id": config_id, "status": status, "result": result},
        )
        response = requests.put(
            f"{self.base_config.scheduler}/run/{run_id}", json=update_schema.dict()
        )
        return response.status_code, response.text

    def stop(self, *args) -> None:
        self.logger.info("Shutting down. Please hold the line...")
        if self.broker_thread:
            self.broker.stop()
            self.broker_thread.join()
        self.heartbeat.stop()
        self.heartbeat.join()


class Heartbeat(threading.Thread):
    def __init__(
        self, scheduler: str, connector_instance: str, log_level: str, interval: int
    ):
        threading.Thread.__init__(self)
        self.scheduler = scheduler
        self.connector_instance = connector_instance
        # self.connector_id = connector_id
        self.interval = interval
        self.logger = get_logger("ConnectorHeartbeat", log_level)

        self.s = sched.scheduler(time.time, time.sleep)
        self.event = self.s.enter(self.interval, 1, self.run_heartbeat)

    def run(self):
        self.s.run()

    def stop(self):
        self.remove_instance()
        try:
            self.s.cancel(self.event)
        except ValueError as e:
            self.logger.error("Killing didn't go as planned")

    def run_heartbeat(self):
        response = requests.put(
            url=f"{self.scheduler}/heartbeat/{self.connector_instance}",
        )

        if response.status_code != 201:
            self.logger.error(f"Heartbeat error {response.status_code}")
            self.event = self.s.enter(self.interval, 1, self.run_heartbeat)
            return
        #
        # if response.text != "OK":
        #     self.logger.error(f"Heartbeat error {response.text}")
        #     self.event = self.s.enter(self.interval, 1, self.run_heartbeat)
        #     return

        self.logger.debug(f"Successful heartbeat {response.text}")

        self.event = self.s.enter(self.interval, 1, self.run_heartbeat)

    def remove_instance(self):
        response = requests.delete(
            url=f"{self.scheduler}/heartbeat/{self.connector_instance}"
        )

        if response.status_code != 204:
            self.logger.error(f"Heartbeat delete error {response.status_code}")
            return

        self.logger.debug(f"Successful heartbeat removal {response.text}")
