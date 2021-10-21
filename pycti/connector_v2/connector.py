import base64
import datetime
import json
import logging
import os
import ssl
import threading
import uuid
from enum import Enum
from typing import List, Dict, Union, Optional, Callable

import yaml

from pycti import OpenCTIApiClient, OpenCTIStix2Splitter
from pycti.connector_v2.libs.messaging.messaging_queue import MessagingQueue

TRUTHY: List[str] = ["yes", "true", "True"]
FALSY: List[str] = ["no", "false", "False"]


class Connector(object):
    def __init__(self):
        self.config = None
        self.logger = None
        self.messaging_queue = None
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = base_path + "/../config.yml"
        self._parse_config(config_file_path)

    def _parse_config(self, config_file_path: str):
        config = (
            yaml.load(open(config_file_path), Loader=yaml.SafeLoader)
            if os.path.isfile(config_file_path)
            else {}
        )
        # Load API config
        self.opencti_url = self.get_config_variable(
            "OPENCTI_URL", ["opencti", "url"], config
        )
        self.opencti_token = self.get_config_variable(
            "OPENCTI_TOKEN", ["opencti", "token"], config
        )
        self.opencti_ssl_verify = self.get_config_variable(
            "OPENCTI_SSL_VERIFY", ["opencti", "ssl_verify"], config, False, True
        )
        self.opencti_json_logging = self.get_config_variable(
            "OPENCTI_JSON_LOGGING", ["opencti", "json_logging"], config
        )
        # Load connector config
        self.connect_id = self.get_config_variable(
            "CONNECTOR_ID", ["connector", "id"], config
        )
        self.connect_type = self.get_config_variable(
            "CONNECTOR_TYPE", ["connector", "type"], config
        )
        self.connect_live_stream_id = self.get_config_variable(
            "CONNECTOR_LIVE_STREAM_ID",
            ["connector", "live_stream_id"],
            config,
            False,
            None,
        )
        self.connect_name = self.get_config_variable(
            "CONNECTOR_NAME", ["connector", "name"], config
        )
        self.connect_confidence_level = self.get_config_variable(
            "CONNECTOR_CONFIDENCE_LEVEL",
            ["connector", "confidence_level"],
            config,
            True,
        )
        self.connect_scope = self.get_config_variable(
            "CONNECTOR_SCOPE", ["connector", "scope"], config
        )
        self.connect_auto = self.get_config_variable(
            "CONNECTOR_AUTO", ["connector", "auto"], config, False, False
        )
        self.connect_only_contextual = self.get_config_variable(
            "CONNECTOR_ONLY_CONTEXTUAL",
            ["connector", "only_contextual"],
            config,
            False,
            False,
        )
        self.log_level = self.get_config_variable(
            "CONNECTOR_LOG_LEVEL", ["connector", "log_level"], config
        )
        self.connect_run_and_terminate = self.get_config_variable(
            "CONNECTOR_RUN_AND_TERMINATE",
            ["connector", "run_and_terminate"],
            config,
            False,
            False,
        )

        # Configure logger
        numeric_level = getattr(
            logging, self.log_level.upper() if self.log_level else "INFO", None
        )
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")
        logging.basicConfig(level=numeric_level)

        # Initialize configuration
        self.api = OpenCTIApiClient(
            self.opencti_url,
            self.opencti_token,
            self.log_level,
            json_logging=self.opencti_json_logging,
        )
        # Register the connector in OpenCTI
        self.connector = ConnectorGraphQLHandler(
            self.connect_id,
            self.connect_name,
            self.connect_type,
            self.connect_scope,
            self.connect_auto,
            self.connect_only_contextual,
        )
        connector_configuration = self.api.connector.register(self.connector)
        logging.info("%s", f"Connector registered with ID: {self.connect_id}")
        self.connector_id = connector_configuration["id"]
        self.work_id = None
        self.applicant_id = connector_configuration["connector_user"]["id"]
        self.connector_state = connector_configuration["connector_state"]
        self.config = connector_configuration["config"]

        # Start ping thread
        if not self.connect_run_and_terminate:
            self.ping = ConnectorPingHandler(
                self.connector.id, self.api, self.get_state, self.set_state
            )
            self.ping.start()

        # self.listen_stream = None
        self.listen_queue = None

    def stop(self) -> None:
        if self.listen_queue:
            self.listen_queue.stop()
        if self.listen_stream:
            self.listen_stream.stop()
        self.ping.stop()
        self.api.connector.unregister(self.connector_id)

    def get_name(self) -> Optional[Union[bool, int, str]]:
        return self.connect_name

    def get_only_contextual(self) -> Optional[Union[bool, int, str]]:
        return self.connect_only_contextual

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
        except:  # pylint: disable=bare-except
            pass
        return None

    def listen(self, messaging_queue: Callable, message_callback: Callable[[Dict], str]) -> None:
        """listen for messages and register callback function

        :param message_callback: callback function to process messages
        :type message_callback: Callable[[Dict], str]
        """

        self.listen_queue = messaging_queue(self, self.config, message_callback)
        self.listen_queue.start()

    def listen_stream(
            self,
            messaging_stream: Callable,
            message_callback,
            url=None,
            token=None,
            verify_ssl=None,
            start_timestamp=None,
            live_stream_id=None,
    ) -> Callable:
        """listen for messages and register callback function

        :param message_callback: callback function to process messages
        """

        self.listen_stream = messaging_stream(
            self,
            message_callback,
            url,
            token,
            verify_ssl,
            start_timestamp,
            live_stream_id,
        )
        self.listen_stream.start()
        return self.listen_stream

    def get_opencti_url(self) -> Optional[Union[bool, int, str]]:
        return self.opencti_url

    def get_opencti_token(self) -> Optional[Union[bool, int, str]]:
        return self.opencti_token

    def get_connector(self) -> ConnectorGraphQLHandler:
        return self.connector

    def log_error(self, msg: str) -> None:
        logging.error(msg)

    def log_info(self, msg: str) -> None:
        logging.info(msg)

    def log_debug(self, msg: str) -> None:
        logging.debug(msg)

    def log_warning(self, msg: str) -> None:
        logging.warning(msg)

    def date_now(self) -> str:
        """get the current date (UTC)
        :return: current datetime for utc
        :rtype: str
        """
        return (
            datetime.datetime.utcnow()
                .replace(microsecond=0, tzinfo=datetime.timezone.utc)
                .isoformat()
        )

        # Push Stix2 helper

    def send_stix2_bundle(self, bundle, **kwargs) -> List:
        """send a stix2 bundle to the API

        :param work_id: a valid work id
        :param bundle: valid stix2 bundle
        :type bundle:
        :param entities_types: list of entities, defaults to None
        :type entities_types: list, optional
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :raises ValueError: if the bundle is empty
        :return: list of bundles
        :rtype: list
        """
        work_id = kwargs.get("work_id", self.work_id)
        entities_types = kwargs.get("entities_types", None)
        update = kwargs.get("update", False)
        event_version = kwargs.get("event_version", None)

        if entities_types is None:
            entities_types = []
        stix2_splitter = OpenCTIStix2Splitter()
        bundles = stix2_splitter.split_bundle(bundle, True, event_version)
        if len(bundles) == 0:
            raise ValueError("Nothing to import")
        if work_id is not None:
            self.api.work.add_expectations(work_id, len(bundles))

        return bundles

    def split_stix2_bundle(self, bundle) -> list:
        """splits a valid stix2 bundle into a list of bundles

        :param bundle: valid stix2 bundle
        :type bundle:
        :raises Exception: if data is not valid JSON
        :return: returns a list of bundles
        :rtype: list
        """

        self.cache_index = {}
        self.cache_added = []
        try:
            bundle_data = json.loads(bundle)
        except Exception as e:
            raise Exception("File data is not a valid JSON") from e

        # validation = validate_parsed_json(bundle_data)
        # if not validation.is_valid:
        #     raise ValueError('The bundle is not a valid STIX2 JSON:' + bundle)

        # Index all objects by id
        for item in bundle_data["objects"]:
            self.cache_index[item["id"]] = item

        bundles = []
        # Reports must be handled because of object_refs
        for item in bundle_data["objects"]:
            if item["type"] == "report":
                items_to_send = self.stix2_deduplicate_objects(
                    self.stix2_get_report_objects(item)
                )
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send["id"])
                bundles.append(self.stix2_create_bundle(items_to_send))

        # Relationships not added in previous reports
        for item in bundle_data["objects"]:
            if item["type"] == "relationship" and item["id"] not in self.cache_added:
                items_to_send = self.stix2_deduplicate_objects(
                    self.stix2_get_relationship_objects(item)
                )
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send["id"])
                bundles.append(self.stix2_create_bundle(items_to_send))

        # Entities not added in previous reports and relationships
        for item in bundle_data["objects"]:
            if item["type"] != "relationship" and item["id"] not in self.cache_added:
                items_to_send = self.stix2_deduplicate_objects(
                    self.stix2_get_entity_objects(item)
                )
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send["id"])
                bundles.append(self.stix2_create_bundle(items_to_send))

        return bundles

    def stix2_get_embedded_objects(self, item) -> Dict:
        """gets created and marking refs for a stix2 item

        :param item: valid stix2 item
        :type item:
        :return: returns a dict of created_by of object_marking_refs
        :rtype: Dict
        """
        # Marking definitions
        object_marking_refs = []
        if "object_marking_refs" in item:
            for object_marking_ref in item["object_marking_refs"]:
                if object_marking_ref in self.cache_index:
                    object_marking_refs.append(self.cache_index[object_marking_ref])
        # Created by ref
        created_by_ref = None
        if "created_by_ref" in item and item["created_by_ref"] in self.cache_index:
            created_by_ref = self.cache_index[item["created_by_ref"]]

        return {
            "object_marking_refs": object_marking_refs,
            "created_by_ref": created_by_ref,
        }

    def stix2_get_entity_objects(self, entity) -> list:
        """process a stix2 entity

        :param entity: valid stix2 entity
        :type entity:
        :return: entity objects as list
        :rtype: list
        """

        items = [entity]
        # Get embedded objects
        embedded_objects = self.stix2_get_embedded_objects(entity)
        # Add created by ref
        if embedded_objects["created_by_ref"] is not None:
            items.append(embedded_objects["created_by_ref"])
        # Add marking definitions
        if len(embedded_objects["object_marking_refs"]) > 0:
            items = items + embedded_objects["object_marking_refs"]

        return items

    def stix2_get_relationship_objects(self, relationship) -> list:
        """get a list of relations for a stix2 relationship object

        :param relationship: valid stix2 relationship
        :type relationship:
        :return: list of relations objects
        :rtype: list
        """

        items = [relationship]
        # Get source ref
        if relationship["source_ref"] in self.cache_index:
            items.append(self.cache_index[relationship["source_ref"]])

        # Get target ref
        if relationship["target_ref"] in self.cache_index:
            items.append(self.cache_index[relationship["target_ref"]])

        # Get embedded objects
        embedded_objects = self.stix2_get_embedded_objects(relationship)
        # Add created by ref
        if embedded_objects["created_by"] is not None:
            items.append(embedded_objects["created_by"])
        # Add marking definitions
        if len(embedded_objects["object_marking_refs"]) > 0:
            items = items + embedded_objects["object_marking_refs"]

        return items

    def stix2_get_report_objects(self, report) -> list:
        """get a list of items for a stix2 report object

        :param report: valid stix2 report object
        :type report:
        :return: list of items for a stix2 report object
        :rtype: list
        """

        items = [report]
        # Add all object refs
        for object_ref in report["object_refs"]:
            items.append(self.cache_index[object_ref])
        for item in items:
            if item["type"] == "relationship":
                items = items + self.stix2_get_relationship_objects(item)
            else:
                items = items + self.stix2_get_entity_objects(item)
        return items

    @staticmethod
    def stix2_deduplicate_objects(items) -> list:
        """deduplicate stix2 items

        :param items: valid stix2 items
        :type items:
        :return: de-duplicated list of items
        :rtype: list
        """

        ids = []
        final_items = []
        for item in items:
            if item["id"] not in ids:
                final_items.append(item)
                ids.append(item["id"])
        return final_items

    @staticmethod
    def stix2_create_bundle(items) -> Optional[str]:
        """create a stix2 bundle with items

        :param items: valid stix2 items
        :type items:
        :return: JSON of the stix2 bundle
        :rtype:
        """

        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "spec_version": "2.0",
            "objects": items,
        }
        return json.dumps(bundle)

    @staticmethod
    def check_max_tlp(tlp: str, max_tlp: str) -> bool:
        """check the allowed TLP levels for a TLP string

        :param tlp: string for TLP level to check
        :type tlp: str
        :param max_tlp: the highest allowed TLP level
        :type max_tlp: str
        :return: TLP level in allowed TLPs
        :rtype: bool
        """

        allowed_tlps: Dict[str, List[str]] = {
            "TLP:RED": ["TLP:WHITE", "TLP:GREEN", "TLP:AMBER", "TLP:RED"],
            "TLP:AMBER": ["TLP:WHITE", "TLP:GREEN", "TLP:AMBER"],
            "TLP:GREEN": ["TLP:WHITE", "TLP:GREEN"],
            "TLP:WHITE": ["TLP:WHITE"],
        }

        return tlp in allowed_tlps[max_tlp]

    @staticmethod
    def get_config_variable(
            env_var: str,
            yaml_path: List,
            config: Dict = None,
            isNumber: Optional[bool] = False,
            default=None,
    ) -> Union[bool, int, None, str]:
        """[summary]

        :param env_var: environnement variable name
        :param yaml_path: path to yaml config
        :param config: client config dict, defaults to None
        :param isNumber: specify if the variable is a number, defaults to False
        """

        if config is None:
            config = {}
        if os.getenv(env_var) is not None:
            result = os.getenv(env_var)
        elif yaml_path is not None:
            if yaml_path[0] in config and yaml_path[1] in config[yaml_path[0]]:
                result = config[yaml_path[0]][yaml_path[1]]
            else:
                return default
        else:
            return default

        if result in TRUTHY:
            return True
        if result in FALSY:
            return False
        if isNumber:
            return int(result)

        return result


    # Scope definition
    # EXTERNAL_IMPORT = None
    # INTERNAL_IMPORT_FILE = Files mime types to support (application/json, ...)
    # INTERNAL_ENRICHMENT = Entity types to support (Report, Hash, ...)
    # INTERNAL_EXPORT_FILE = Files mime types to generate (application/pdf, ...)
    # STREAM = none

class ConnectorType(Enum):
        EXTERNAL_IMPORT = "EXTERNAL_IMPORT"  # From remote sources to OpenCTI stix2
        INTERNAL_IMPORT_FILE = (
            "INTERNAL_IMPORT_FILE"  # From OpenCTI file system to OpenCTI stix2
        )
        INTERNAL_ENRICHMENT = "INTERNAL_ENRICHMENT"  # From OpenCTI stix2 to OpenCTI stix2
        INTERNAL_EXPORT_FILE = (
            "INTERNAL_EXPORT_FILE"  # From OpenCTI stix2 to OpenCTI file system
        )
        STREAM = "STREAM"  # Read the stream and do something

class ConnectorGraphQLHandler:
        """Main class for OpenCTI connector

        :param connector_id: id for the connector (valid uuid4)
        :type connector_id: str
        :param connector_name: name for the connector
        :type connector_name: str
        :param connector_type: valid OpenCTI connector type (see `ConnectorType`)
        :type connector_type: str
        :param scope: connector scope
        :type scope: str
        :raises ValueError: if the connector type is not valid
        """

        def __init__(
                self,
                connector_id: str,
                connector_name: str,
                connector_type: str,
                scope: str,
                auto: bool,
                only_contextual: bool,
        ):
            self.id = connector_id
            self.name = connector_name
            self.type = ConnectorType(connector_type)
            if self.type is None:
                raise ValueError("Invalid connector type: " + connector_type)
            if scope and len(scope) > 0:
                self.scope = scope.split(",")
            else:
                self.scope = []
            self.auto = auto
            self.only_contextual = only_contextual

        def to_input(self) -> dict:
            """connector input to use in API query

            :return: dict with connector data
            :rtype: dict
            """
            return {
                "input": {
                    "id": self.id,
                    "name": self.name,
                    "type": self.type.name,
                    "scope": self.scope,
                    "auto": self.auto,
                    "only_contextual": self.only_contextual,
                }
            }


class ConnectorPingHandler(threading.Thread):
    def __init__(self, connector_id, api, get_state, set_state) -> None:
        threading.Thread.__init__(self)
        self.connector_id = connector_id
        self.in_error = False
        self.api = api
        self.get_state = get_state
        self.set_state = set_state
        self.exit_event = threading.Event()

    def ping(self) -> None:
        while not self.exit_event.is_set():
            try:
                initial_state = self.get_state()
                result = self.api.connector.ping(self.connector_id, initial_state)
                remote_state = (
                    json.loads(result["connector_state"])
                    if result["connector_state"] is not None
                       and len(result["connector_state"]) > 0
                    else None
                )
                if initial_state != remote_state:
                    self.set_state(result["connector_state"])
                    logging.info(
                        "%s",
                        (
                            "Connector state has been remotely reset to: "
                            f'"{self.get_state()}"'
                        ),
                    )
                if self.in_error:
                    self.in_error = False
                    logging.error("API Ping back to normal")
            except Exception:  # pylint: disable=broad-except
                self.in_error = True
                logging.error("Error pinging the API")
            self.exit_event.wait(40)

    def run(self) -> None:
        logging.info("Starting ping alive thread")
        self.ping()

    def stop(self) -> None:
        logging.info("Preparing for clean shutdown")
        self.exit_event.set()
