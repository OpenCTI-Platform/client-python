import uuid
from typing import List, Optional
from pydantic import BaseModel
from stix2 import Bundle, IPv4Address
from pycti import StixCyberObservableTypes
from pycti.connector.new.connector_types.connector_settings import ConnectorConfig
from pycti.connector.new.connector_types.connector_base_types import (
    InternalEnrichmentConnector as IEC,
)
from pycti.connector.new.tests.test_class import ConnectorTest


class IEModel(ConnectorConfig):
    pass


class InternalEnrichmentConnector(IEC):
    config = IEModel

    def run(self, entity_id: str, config: BaseModel) -> (str, List[Bundle]):
        ip4 = IPv4Address(value="177.60.40.7")
        bundle = Bundle(ip4, allow_custom=True)
        return "Finished", [bundle]


class InternalEnrichmentTest(ConnectorTest):
    connector = InternalEnrichmentConnector

    def _setup(self, monkeypatch):
        monkeypatch.setenv("opencti_broker", "pika")
        monkeypatch.setenv("opencti_ssl_verify", "False")
        monkeypatch.setenv("connector_name", "Simple Import")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_scope", '["application/pdf"]')
        monkeypatch.setenv("connector_testing", "True")

        self.ipv4 = self.api_client.stix_cyber_observable.create(
            observableData={
                "type": "ipv4-addr",
                "value": "8.8.8.8",
            }
        )

    def teardown(self):
        self.api_client.stix_cyber_observable.delete(id=self.ipv4["id"])

    def initiate(self) -> Optional[str]:
        work_id = self.api_client.stix_cyber_observable.ask_for_enrichment(
            id=self.ipv4["id"],
            connector_id=self.connector_instance.base_config.id,
        )
        return work_id

    def verify(self, bundle: Bundle):
        bundle_objects = bundle["objects"]
        assert len(bundle_objects) == 1, "Bundle size is not equal to 1"
        for _object in bundle_objects:
            assert (
                _object["type"]
                == StixCyberObservableTypes.IPV4_ADDR.value.__str__().lower()
            ), "Object not an IPv4Addr"
            assert _object["value"] == "177.60.40.7", "IPv4 has wrong IP"
