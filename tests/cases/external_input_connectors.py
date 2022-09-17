import json
import threading
import uuid
from typing import List
from stix2 import Bundle
from pycti import StixMetaTypes
from pycti.connector.new.connector_types.connector_settings import ConnectorConfig
from pycti.connector.new.connector_types.connector_base_types import (
    ExternalInputConnector as EIC,
)
from pycti.connector.new.libs.mixins.http import HttpMixin
from tests.cases.connector_test_class import ConnectorTest

class EIModel(ConnectorConfig):
    url: str


class ExternalInputConnector(EIC, HttpMixin):
    config = EIModel

    def run(self, config: EIModel) -> (str, List[Bundle]):
        url = config.url
        content = self.get(url)
        bundle = Bundle(**json.loads(content), allow_custom=True)
        return "Finished", [bundle]


class ExternalInputTest(ConnectorTest):
    connector = ExternalInputConnector

    def setup(self, monkeypatch):
        monkeypatch.setenv("opencti_url", self.api_client.opencti_url)
        monkeypatch.setenv("opencti_token", self.api_client.api_token)
        monkeypatch.setenv("opencti_broker", "pika")
        monkeypatch.setenv("opencti_ssl_verify", "False")
        monkeypatch.setenv("connector_name", "Simple Import")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_name", "Get STIX Github Connector")
        monkeypatch.setenv("connector_run_and_terminate", "true")
        monkeypatch.setenv("connector_interval", "2")
        monkeypatch.setenv("connector_testing", "True")
        monkeypatch.setenv(
            "app_url",
            "https://github.com/oasis-open/cti-stix-common-objects/raw/main/objects/marking-definition/marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf.json",
        )

    def teardown(self):
        pass
        # TODO remove marking definition

    def verify(self, bundle: Bundle):
        bundle_objects = bundle["objects"]
        assert len(bundle_objects) == 1, "Bundle size is not equal to 1"
        for _object in bundle_objects:
            assert (
                _object["type"]
                == StixMetaTypes.MARKING_DEFINITION.value.__str__().lower()
            ), "Object not a Marking Definition"
            assert (
                _object["id"]
                == "marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf"
            ), "Object has wrong ID"
