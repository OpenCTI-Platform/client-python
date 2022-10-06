import uuid
from typing import List, Optional

from pydantic import BaseModel
from stix2 import Bundle, IPv4Address
from dateutil.parser import parse

from pycti import StixCyberObservableTypes
from pycti.connector.new.connector_types.connector_settings import ConnectorConfig
from pycti.connector.new.connector_types.connector_base_types import (
    InternalFileInputConnector,
)
from pycti.connector.new.tests.test_class import ConnectorTest


class IIModel(ConnectorConfig):
    pass


class InternalInputConnector(InternalFileInputConnector):
    config = IIModel

    def run(
        self, file_path: str, file_mime: str, entity_id: str, config: IIModel
    ) -> (str, List[Bundle]):
        self.logger.info(f"Processing file: {file_path} ({file_mime})")
        ip4 = IPv4Address(value="177.60.40.7")
        bundle = Bundle(ip4)
        return "Finished", [bundle]


class InternalFileInputTest(ConnectorTest):
    connector = InternalInputConnector

    def _setup(self, monkeypatch):
        monkeypatch.setenv("opencti_broker", "pika")
        monkeypatch.setenv("opencti_ssl_verify", "False")
        monkeypatch.setenv("connector_name", "Simple Import")
        monkeypatch.setenv("connector_id", str(uuid.uuid4()))
        monkeypatch.setenv("connector_scope", "application/pdf")
        monkeypatch.setenv("connector_testing", "True")

        date = parse("2019-12-01").strftime("%Y-%m-%dT%H:%M:%SZ")
        self.organization = self.api_client.identity.create(
            type="Organization",
            name="My organization",
            alias=["my-organization"],
            description="A new organization.",
        )

        # Create the report
        self.report = self.api_client.report.create(
            name="My new report of my organization",
            description="A report wrote by my organization",
            published=date,
            report_types=["internal-report"],
            createdBy=self.organization["id"],
        )

        self.file = self.api_client.stix_domain_object.add_file(
            id=self.report["id"],
            file_name="./tests/integration/support_data/test.pdf",
        )

    def teardown(self):
        self.api_client.stix_domain_object.delete(id=self.report["id"])
        self.api_client.stix_domain_object.delete(id=self.organization["id"])

    def initiate(self) -> Optional[str]:
        file_url = self.api_client.stix_domain_object.file_ask_for_enrichment(
            file_id=self.file["data"]["stixDomainObjectEdit"]["importPush"]["id"],
            connector_id=self.connector_instance.base_config.id,
        )
        return None

    def verify(self, bundle: Bundle):
        bundle_objects = bundle["objects"]
        assert len(bundle_objects) == 1, "Bundle size is not equal to 1"
        for _object in bundle_objects:
            assert (
                _object["type"]
                == StixCyberObservableTypes.IPV4_ADDR.value.__str__().lower()
            ), "Object not an IPv4Addr"
            assert _object["value"] == "177.60.40.7", "IPv4 has wrong IP"
