import datetime
import threading
import pika
import logging
import json
import time
import base64
import os

from typing import Callable, Dict, List, Optional, Union
from pika.exceptions import UnroutableError, NackError
from pycti.api.opencti_api_client import OpenCTIApiClient
from pycti.connector.opencti_connector import OpenCTIConnector
from utils.splix_splitter import StixSplitter


def get_config_variable(
    env_var: str, yaml_path: list, config: Dict = {}, isNumber: Optional[bool] = False
) -> Union[bool, int, None, str]:
    """[summary]

    :param env_var: environnement variable name
    :param yaml_path: path to yaml config
    :param config: client config dict, defaults to {}
    :param isNumber: specify if the variable is a number, defaults to False
    """

    if os.getenv(env_var) is not None:
        result = os.getenv(env_var)
    elif yaml_path is not None:
        if yaml_path[0] in config and yaml_path[1] in config[yaml_path[0]]:
            result = config[yaml_path[0]][yaml_path[1]]
        else:
            return None
    else:
        return None

    if result == "yes" or result == "true" or result == "True":
        return True
    elif result == "no" or result == "false" or result == "False":
        return False
    elif isNumber:
        return int(result)
    else:
        return result


class ListenQueue(threading.Thread):
    """Main class for the ListenQueue used in OpenCTIConnectorHelper

    :param helper: instance of a `OpenCTIConnectorHelper` class
    :type helper: OpenCTIConnectorHelper
    :param config: dict containing client config
    :type config: dict
    :param callback: callback function to process queue
    :type callback: callable
    """

    def __init__(self, helper, config: dict, callback):
        threading.Thread.__init__(self)
        self.pika_connection = None
        self.channel = None
        self.helper = helper
        self.callback = callback
        self.uri = config["uri"]
        self.queue_name = config["listen"]

    # noinspection PyUnusedLocal
    def _process_message(self, channel, method, properties, body):
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
        thread = threading.Thread(target=self._data_handler, args=[json_data])
        thread.start()
        while thread.is_alive():  # Loop while the thread is processing
            self.pika_connection.sleep(1.0)
        logging.info(
            "Message (delivery_tag="
            + str(method.delivery_tag)
            + ") processed, thread terminated"
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _data_handler(self, json_data):
        job_id = json_data["job_id"] if "job_id" in json_data else None
        try:
            work_id = json_data["work_id"]
            self.helper.current_work_id = work_id
            self.helper.api.job.update_job(job_id, "progress", ["Starting process"])
            messages = self.callback(json_data)
            self.helper.api.job.update_job(job_id, "complete", messages)
        except Exception as e:
            logging.exception("Error in message processing, reporting error to API")
            try:
                self.helper.api.job.update_job(job_id, "error", [str(e)])
            except:
                logging.error("Failing reporting the processing")

    def run(self):
        while True:
            try:
                # Connect the broker
                self.pika_connection = pika.BlockingConnection(
                    pika.URLParameters(self.uri)
                )
                self.channel = self.pika_connection.channel()
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except (KeyboardInterrupt, SystemExit):
                self.helper.log_info("Connector stop")
                exit(0)
            except Exception as e:
                self.helper.log_error(str(e))
                time.sleep(10)


class PingAlive(threading.Thread):
    def __init__(self, connector_id, api, get_state, set_state):
        threading.Thread.__init__(self)
        self.connector_id = connector_id
        self.in_error = False
        self.api = api
        self.get_state = get_state
        self.set_state = set_state

    def ping(self):
        while True:
            try:
                initial_state = self.get_state()
                result = self.api.connector.ping(self.connector_id, initial_state)
                remote_state = (
                    json.loads(result["connector_state"])
                    if len(result["connector_state"]) > 0
                    else None
                )
                if initial_state != remote_state:
                    self.set_state(result["connector_state"])
                    logging.info(
                        'Connector state has been remotely reset to: "'
                        + self.get_state()
                        + '"'
                    )
                if self.in_error:
                    self.in_error = False
                    logging.error("API Ping back to normal")
            except Exception:
                self.in_error = True
                logging.error("Error pinging the API")
            time.sleep(40)

    def run(self):
        logging.info("Starting ping alive thread")
        self.ping()


class OpenCTIConnectorHelper:
    """Python API for OpenCTI connector

    :param config: Dict standard config
    :type config: dict
    """

    def __init__(self, config: dict):
        # Load API config
        self.opencti_url = get_config_variable(
            "OPENCTI_URL", ["opencti", "url"], config
        )
        self.opencti_token = get_config_variable(
            "OPENCTI_TOKEN", ["opencti", "token"], config
        )
        # Load connector config
        self.connect_id = get_config_variable(
            "CONNECTOR_ID", ["connector", "id"], config
        )
        self.connect_type = get_config_variable(
            "CONNECTOR_TYPE", ["connector", "type"], config
        )
        self.connect_name = get_config_variable(
            "CONNECTOR_NAME", ["connector", "name"], config
        )
        self.connect_confidence_level = get_config_variable(
            "CONNECTOR_CONFIDENCE_LEVEL",
            ["connector", "confidence_level"],
            config,
            True,
        )
        self.connect_scope = get_config_variable(
            "CONNECTOR_SCOPE", ["connector", "scope"], config
        )
        self.log_level = get_config_variable(
            "CONNECTOR_LOG_LEVEL", ["connector", "log_level"], config
        )

        # Configure logger
        numeric_level = getattr(logging, self.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: " + self.log_level)
        logging.basicConfig(level=numeric_level)

        # Initialize configuration
        self.api = OpenCTIApiClient(
            self.opencti_url, self.opencti_token, self.log_level
        )
        self.current_work_id = None

        # Register the connector in OpenCTI
        self.connector = OpenCTIConnector(
            self.connect_id, self.connect_name, self.connect_type, self.connect_scope
        )
        connector_configuration = self.api.connector.register(self.connector)
        self.connector_id = connector_configuration["id"]
        self.connector_state = connector_configuration["connector_state"]
        self.config = connector_configuration["config"]

        # Start ping thread
        self.ping = PingAlive(
            self.connector.id, self.api, self.get_state, self.set_state
        )
        self.ping.start()

    def set_state(self, state) -> None:
        """sets the connector state

        :param state: state object
        :type state: dict
        """

        self.connector_state = json.dumps(state)

    def get_state(self):
        """get the connector state

        :return: returns the current state of the connector if there is any
        :rtype:
        """

        try:
            return (
                None
                if self.connector_state is None
                else json.loads(self.connector_state)
            )
        except:
            return None

    def listen(self, message_callback: Callable[[Dict], List[str]]) -> None:
        """listen for messages and register callback function

        :param message_callback: callback function to process messages
        :type message_callback: Callable[[Dict], List[str]]
        """

        listen_queue = ListenQueue(self, self.config, message_callback)
        listen_queue.start()

    def get_connector(self):
        return self.connector

    def log_error(self, msg):
        logging.error(msg)

    def log_info(self, msg):
        logging.info(msg)

    def date_now(self) -> str:
        """get the current date (UTC)
        :return: current datetime for utc
        :rtype: str
        """
        return datetime.datetime.utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()

    # Push Stix2 helper
    def send_stix2_bundle(
        self, bundle, entities_types=None, update=False, split=True
    ) -> list:
        """send a stix2 bundle to the API

        :param bundle: valid stix2 bundle
        :type bundle:
        :param entities_types: list of entities, defaults to None
        :type entities_types: list, optional
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :param split: whether to split the stix bundle before processing, defaults to True
        :type split: bool, optional
        :raises ValueError: if the bundle is empty
        :return: list of bundles
        :rtype: list
        """

        if entities_types is None:
            entities_types = []
        if split:
            stix_splitter = StixSplitter()
            bundles = stix_splitter.split_bundle(bundle)
            if len(bundles) == 0:
                raise ValueError("Nothing to import")
            pika_connection = pika.BlockingConnection(
                pika.URLParameters(self.config["uri"])
            )
            channel = pika_connection.channel()
            for bundle in bundles:
                self._send_bundle(channel, bundle, entities_types, update)
            channel.close()
            return bundles
        else:
            pika_connection = pika.BlockingConnection(
                pika.URLParameters(self.config["uri"])
            )
            channel = pika_connection.channel()
            self._send_bundle(channel, bundle, entities_types, update)
            channel.close()
            return [bundle]

    def _send_bundle(self, channel, bundle, entities_types=None, update=False) -> None:
        """send a STIX2 bundle to RabbitMQ to be consumed by workers

        :param channel: RabbitMQ channel
        :type channel: callable
        :param bundle: valid stix2 bundle
        :type bundle:
        :param entities_types: list of entity types, defaults to None
        :type entities_types: list, optional
        :param update: whether to update data in the database, defaults to False
        :type update: bool, optional
        """

        if entities_types is None:
            entities_types = []

        # Create a job log expectation
        if self.current_work_id is not None:
            job_id = self.api.job.initiate_job(self.current_work_id)
        else:
            job_id = None

        # Validate the STIX 2 bundle
        # validation = validate_string(bundle)
        # if not validation.is_valid:
        # raise ValueError('The bundle is not a valid STIX2 JSON')

        # Prepare the message
        # if self.current_work_id is None:
        #    raise ValueError('The job id must be specified')
        message = {
            "job_id": job_id,
            "entities_types": entities_types,
            "update": update,
            "token": self.opencti_token,
            "content": base64.b64encode(bundle.encode("utf-8")).decode("utf-8"),
        }

        # Send the message
        try:
            routing_key = "push_routing_" + self.connector_id
            channel.basic_publish(
                exchange=self.config["push_exchange"],
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            logging.info("Bundle has been sent")
        except (UnroutableError, NackError) as e:
            logging.error(f"Unable to send bundle, retry...{e}")
            self._send_bundle(bundle, entities_types)

    @staticmethod
    def check_max_tlp(tlp, max_tlp) -> bool:
        """check the allowed TLP levels for a TLP string

        :param tlp: string for TLP level to check
        :type tlp: str
        :param max_tlp: the highest allowed TLP level
        :type max_tlp: str
        :return: list of allowed TLP levels
        :rtype: bool
        """

        allowed_tlps = ["TLP:WHITE"]
        if max_tlp == "TLP:RED":
            allowed_tlps = ["TLP:WHITE", "TLP:GREEN", "TLP:AMBER", "TLP:RED"]
        elif max_tlp == "TLP:AMBER":
            allowed_tlps = ["TLP:WHITE", "TLP:GREEN", "TLP:AMBER"]
        elif max_tlp == "TLP:GREEN":
            allowed_tlps = ["TLP:WHITE", "TLP:GREEN"]

        return tlp in allowed_tlps
