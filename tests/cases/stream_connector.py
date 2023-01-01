import uuid
from typing import List, Optional

from sseclient import Event
from stix2 import Bundle, IPv4Address

from pycti.connector.connector_types.connector_base_types import StreamInputConnector
from pycti.connector.connector_types.connector_settings import ConnectorConfig
from pycti.test_plugin.test_class import ConnectorTest


class StreamModel(ConnectorConfig):
    url: str


class StreamConnector(StreamInputConnector):
    scope = "testbus"
    config = StreamModel
    bundle = Bundle(IPv4Address(value="177.60.40.1"), allow_custom=True)

    def run(
        self, config: StreamModel, msg: Event
    ) -> (Optional[str], Optional[List[Bundle]]):
        self.logger.info(f"Received message: {msg}")
        return "Finished", [self.bundle]
        # return "1234", []


class StreamConnectorTest(ConnectorTest):
    connector = StreamConnector
    bundle = Bundle(IPv4Address(value="177.60.40.1"), allow_custom=True)

    def _setup(self, monkeypatch):
        monkeypatch.setenv("opencti_ssl_verify", "False")
        monkeypatch.setenv("connector_name", "Test Stream Connector")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_testing", "True")
        monkeypatch.setenv(
            "app_url",
            "https://github.com/oasis-open/cti-stix-common-objects/raw/main/objects/marking-definition/marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf.json",
        )
