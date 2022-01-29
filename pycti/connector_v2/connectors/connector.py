import json
import logging
import threading
from typing import List, Dict, Union, Optional, Any, Callable, Type

from celery import Task
from pydantic import create_model, BaseSettings

from pycti import OpenCTIApiClient, OpenCTIStix2Splitter
from pycti.connector_v2.libs.pika_broker import PikaBroker
from pycti.connector_v2.libs.connector_utils import get_logger, ConnectorType

class ConnectorSettings(BaseSettings):
    opencti_url: str
    opencti_ssl_verify: bool = True
    connector_id: str
    connector_name: str



class OpenCTIBaseSettings(BaseSettings):
    opencti_url: str
    opencti_token: str
    opencti_ssl_verify: bool = True

#     class Config:
#         env_prefix = "opencti_"
#
#
# class ConnectorBaseSettings(BaseSettings):
    connector_id: str
    connector_name: str
    connector_type: str
    connector_json_logging: bool = False
    connector_log_level: str = "INFO"
    # TODO possible removal in the future
    connector_only_contextual: bool = False
    connector_auto: bool = False
    connector_scope: str = ""

    # class Config:
    #     env_prefix = "connector_"


# Scope definition
# EXTERNAL_IMPORT = None
# INTERNAL_IMPORT_FILE = Files mime types to support (application/json, ...)
# INTERNAL_ENRICHMENT = Entity types to support (Report, Hash, ...)
# INTERNAL_EXPORT_FILE = Files mime types to generate (application/pdf, ...)
# STREAM = none


class ApplicationSettings(BaseSettings):
    class Config:
        env_prefix = "app_"


# TODO OpenCTI, Connector and APP settings come via constructor
# TODO only value getting from env/yaml is the celery scheduler location (hmm and maybe more, opencti token?)
# TODO for worker and connector manager create minimal "NakedConnector" Class

class Connector(Task):
    def __init__(
        self,
        connector_model: Type[ConnectorBaseSettings],
        application_model: Type[ApplicationSettings],
    ):
        # Connector sub objects
        self.api = None
        self.graphql_connector = None
        self.messaging_broker = None
        self.ping = None

        # Connector instance infos
        self.config = None

        self.connector_state = None

        # Run test configs if present
        self.connector_settings = create_model(
            "ConnectorSettings",
            opencti=(OpenCTIBaseSettings, ...),
            connector=(connector_model, ...),
            app=(application_model, ...),
        )
        self.connector_model = connector_model
        self.application_model = application_model

        # Initialize configuration
        self.config = self.connector_settings(
            opencti=OpenCTIBaseSettings(),
            connector=self.connector_model(),
            app=self.application_model(),
        )

        numeric_level = getattr(logging, self.config.connector.log_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.config.connector.log_level}")

        # Init calls
        # self.config, numeric_level = self._load_config()

        self.logger = get_logger(self.config.connector.name, numeric_level)

        self.init()

    def init(self):
        pass

    def start(self) -> None:
        self.api = OpenCTIApiClient(
            self.config.opencti.url,
            self.config.opencti.token,
            self.config.connector.log_level,
            json_logging=self.config.connector.json_logging,
        )
        # Register the connector in OpenCTI
        self.graphql_connector = ConnectorGraphQLHandler(
            self.config.connector.id,
            self.config.connector.name,
            self.config.connector.type,
            self.config.connector.scope,
            self.config.connector.auto,
            self.config.connector.only_contextual,
            self.api,
            self.logger,
        )

        connector_configuration = self.graphql_connector.register()
        self.connector_state = connector_configuration["connector_state"]
        self.logger.info(f"Connector registered with ID: {self.config.connector.id}")

        self.logger.debug("Finished setting up connector")

    def _stop(self):
        pass

    def stop(self) -> None:
        self.logger.info("Shutting down!")
        self._stop()
        # self.ping.stop()
        # self.messaging_broker.stop()
        self._unregister_connector()
        self.logger.info("Connector stopped")

    # def _run(self) -> None:
    #     pass

    def run(self) -> None:
        # TODO make certain run steps connector type dependant
        # When exception, also initiate work.exception
        # TODO handle keyboard kill exception
        pass

    def _unregister_connector(self):
        self.graphql_connector.unregister()

    def send_stix2_bundle(
        self,
        bundle: List,
        work_id: str = None,
        entities_types: List = None,
        update: bool = False,
        event_version: str = None,
    ) -> List:
        """send a stix2 bundle to the API

        :param work_id: a valid work id
        :param bundle: valid stix2 bundle
        :type bundle:
        :param entities_types: list of entities, defaults to None
        :type entities_types: list, optional
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :param event_version: str, defaults to None
        :type event_version: str, optional
        :raises ValueError: if the bundle is empty
        :return: list of bundles
        :rtype: list
        """
        if entities_types is None:
            entities_types = []

        stix2_splitter = OpenCTIStix2Splitter()
        bundles = stix2_splitter.split_bundle(bundle, True, event_version)
        if len(bundles) == 0:
            raise ValueError("Nothing to import")

        # Validate the STIX 2 bundle
        # validation = validate_string(bundle)
        # if not validation.is_valid:
        # raise ValueError('The bundle is not a valid STIX2 JSON')

        if work_id is not None:
            self.api.work.add_expectations(work_id, len(bundles))

        self.messaging_broker.send(work_id, bundles, entities_types, update)

        return bundles

    # TODO figure out if this function should stay
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
        except Exception as e:
            self.logger.error(e, exec_info=True)
        return None

    # Support functions

    def get_name(self) -> Optional[Union[bool, int, str]]:
        return self.config.connector.name

    def get_only_contextual(self) -> Optional[Union[bool, int, str]]:
        return self.config.connector.only_contextual

    def get_opencti_url(self) -> Optional[Union[bool, int, str]]:
        return self.config.opencti.url

    def get_opencti_token(self) -> Optional[Union[bool, int, str]]:
        return self.config.opencti.token


class ConnectorGraphQLHandler:
    """Main class for OpenCTI connector

    :param connector_id: id for the connector (valid uuid4)
    :type connector_id: str
    :param connector_name: name for the connector
    :type connector_name: str
    :param connector_type: valid OpenCTI connector type (see `ConnectorType`)
    :type connector_type: str
    :param scope_value: connector scope
    :type scope_value: str
    :raises ValueError: if the connector type is not valid
    """

    def __init__(
        self,
        connector_id: str,
        connector_name: str,
        connector_type: str,
        scope_value: str = "",
        auto: bool = False,
        only_contextual: bool = False,
        api: OpenCTIApiClient = None,
        logger: logging.Logger = None,
    ):
        self.connector_id = connector_id
        self.name = connector_name
        self.type = ConnectorType(connector_type)
        self.api = api
        self.logger = logger
        if self.type is None:
            raise ValueError("Invalid connector type: " + connector_type)
        if scope_value and len(scope_value) > 0:
            self.scope = scope_value.split(",")
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
                "id": self.connector_id,
                "name": self.name,
                "type": self.type.name,
                "scope": self.scope,
                "auto": self.auto,
                "only_contextual": self.only_contextual,
            }
        }

    def list(self) -> Dict:
        """list available connectors

        :return: return dict with connectors
        :rtype: dict
        """

        self.logger.info("Getting connectors ...")
        query = """
                query GetConnectors {
                    connectors {
                        id
                        name
                        config {
                            connection {
                                host
                                use_ssl
                                port
                                user
                                pass
                            }
                            listen
                            push
                        }
                        connector_user {
                            id
                        }
                    }
                }
            """
        result = self.api.query(query)
        return result["data"]["connectors"]

    def ping(self, connector_state: Any) -> Dict:
        """pings a connector by id and state

        :param connector_state: state for the connector
        :type connector_state:
        :return: the response pingConnector data dict
        :rtype: dict
        """

        query = """
                mutation PingConnector($id: ID!, $state: String) {
                    pingConnector(id: $id, state: $state) {
                        id
                        connector_state
                    }
                }
               """
        result = self.api.query(
            query, {"id": self.connector_id, "state": json.dumps(connector_state)}
        )
        return result["data"]["pingConnector"]

    def register(self) -> Dict:
        """register a connector with OpenCTI

        :return: the response registerConnector data dict
        :rtype: dict
        """

        query = """
                mutation RegisterConnector($input: RegisterConnectorInput) {
                    registerConnector(input: $input) {
                        id
                        connector_state
                        config {
                            connection {
                                host
                                use_ssl
                                port
                                user
                                pass
                            }
                            listen
                            listen_exchange
                            push
                            push_exchange
                        }
                        connector_user {
                            id
                        }
                    }
                }
               """
        result = self.api.query(query, self.to_input())
        return result["data"]["registerConnector"]

    def unregister(self) -> Dict:
        """unregister a connector with OpenCTI

        :return: the response registerConnector data dict
        :rtype: dict
        """
        query = """
                mutation ConnectorDeletionMutation($id: ID!) {
                    deleteConnector(id: $id) 
                }
            """
        return self.api.query(query, {"id": self.connector_id})
