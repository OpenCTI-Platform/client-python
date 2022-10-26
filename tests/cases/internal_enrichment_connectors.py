import uuid
from typing import List, Optional

from pydantic import BaseModel
from stix2 import Bundle, IPv4Address

from pycti.connector.connector_types.connector_base_types import (
    InternalEnrichmentConnector as IEC,
)
from pycti.connector.connector_types.connector_settings import ConnectorConfig
from pycti.connector.tests.test_class import ConnectorTest


class IEModel(ConnectorConfig):
    pass


class InternalEnrichmentConnector(IEC):
    config = IEModel

    def run(self, entity_id: str, config: BaseModel) -> (str, List[Bundle]):
        bundle = Bundle(IPv4Address(value="177.60.40.7"), allow_custom=True)
        return "Finished", [bundle]


class InternalEnrichmentTest(ConnectorTest):
    connector = InternalEnrichmentConnector
    bundle = Bundle(IPv4Address(value="177.60.40.7"), allow_custom=True)

    def _setup(self, monkeypatch):
        monkeypatch.setenv("connector_name", "Simple Import")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_scope", "IPv4-addr,Domain")
        monkeypatch.setenv("connector_testing", "True")
        monkeypatch.setenv("connector_max_tlp", "TLP:AMBER")

        # Create the marking definition
        marking_definition = self.api_client.marking_definition.create(
            definition_type="TLP",
            definition="TLP:CLEAR",
            x_opencti_order=10,
            x_opencti_color="#000000",
        )

        self.ipv4 = self.api_client.stix_cyber_observable.create(
            observableData={
                "type": "ipv4-addr",
                "value": "8.8.8.8",
            }
        )

        self.api_client.stix_cyber_observable.add_marking_definition(
            id=self.ipv4["id"], marking_definition_id=marking_definition["id"]
        )

    def teardown(self):
        self.api_client.stix_cyber_observable.delete(id=self.ipv4["id"])

    def initiate(self) -> Optional[str]:
        work_id = self.api_client.stix_cyber_observable.ask_for_enrichment(
            id=self.ipv4["id"],
            connector_id=self.connector_instance.base_config.id,
        )
        return work_id


class InternalEnrichmentTest_TLP_Invalid(InternalEnrichmentTest):
    connector = InternalEnrichmentConnector

    def _setup(self, monkeypatch):
        monkeypatch.setenv("connector_name", "Simple Import")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_scope", "IPv4-addr,Domain")
        monkeypatch.setenv("connector_testing", "True")
        monkeypatch.setenv("connector_max_tlp", "TLP:AMBER")

        # Create the marking definition
        marking_definition = self.api_client.marking_definition.create(
            definition_type="TLP",
            definition="TLP:RED",
            x_opencti_order=10,
            x_opencti_color="#000000",
        )

        self.ipv4 = self.api_client.stix_cyber_observable.create(
            observableData={
                "type": "ipv4-addr",
                "value": "8.8.8.8",
            }
        )

        self.api_client.stix_cyber_observable.add_marking_definition(
            id=self.ipv4["id"], marking_definition_id=marking_definition["id"]
        )

    @staticmethod
    def get_expected_exception() -> str:
        return "TLP of the observable is greater than MAX TLP"
