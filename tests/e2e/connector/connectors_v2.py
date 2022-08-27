import json
import threading
import time
import uuid
from dateutil.parser import parse
from pydantic import BaseModel
from stix2 import Bundle, IPv4Address

from pycti.connector.new.connector_types.connector_settings import ConnectorConfig
from pycti.connector.new.libs.mixins.http import HttpMixin
from pycti.connector.new.connector_types.connector_base_types import ExternalInputConnector as EIC, InternalFileInputConnector as IFIC


class EIModel(ConnectorConfig):
    url: str


class ExternalInputConnector(EIC, HttpMixin):
    config = EIModel

    def run(self, event: dict, config: EIModel) -> str:
        url = config.url
        content = self.get(url)
        bundle = Bundle(**json.loads(content), allow_custom=True)
        self.send(bundle)
        return "Finished"


def test_external_import_connector(caplog, api_client, opencti_server, monkeypatch):
    monkeypatch.setenv("opencti_url", opencti_server)
    monkeypatch.setenv("opencti_token", "18bd74e5-404c-4216-ac74-23de6249d690")
    monkeypatch.setenv("opencti_broker", "stdout")
    monkeypatch.setenv("opencti_ssl_verify", "False")
    monkeypatch.setenv("connector_name", "Get STIX Github Connector")
    monkeypatch.setenv("connector_run_and_terminate", "true")
    monkeypatch.setenv("connector_interval", "10")
    monkeypatch.setenv("connector_id", str(uuid.uuid4()))
    monkeypatch.setenv("app_url",
                       "https://github.com/oasis-open/cti-stix-common-objects/raw/main/objects/marking-definition/marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf.json")

    connector = ExternalInputConnector()
    t1 = threading.Thread(target=connector.start)
    t1.start()

    time.sleep(1)

    assert "Sending container" in caplog.text, "No container sent"

    connector.stop()
    t1.join()
    api_client.connector.unregister(connector.base_config.id)


### Internal File Import

class IIModel(ConnectorConfig):
    pass


class InternalInputConnector(IFIC):
    config = IIModel

    def run(self, file_path: str, file_mime: str, entity_id: str, config: BaseModel) -> str:
        self.logger.info(f"Processing file: {file_path} ({file_mime})")
        ip4 = IPv4Address(
            value="177.60.40.7"
        )
        bundle = Bundle(ip4)
        self.send(bundle)
        return "Finished"


def test_internal_import_connector(caplog, api_client, opencti_server, monkeypatch):
    monkeypatch.setenv("opencti_url", opencti_server)
    monkeypatch.setenv("opencti_token", "18bd74e5-404c-4216-ac74-23de6249d690")
    monkeypatch.setenv("opencti_broker", "pika")
    monkeypatch.setenv("opencti_ssl_verify", "False")
    monkeypatch.setenv("connector_name", "Simple Import")
    monkeypatch.setenv("connector_id", str(uuid.uuid4()))
    monkeypatch.setenv("connector_scope", "['application/pdf','aaa']")

    date = parse("2019-12-01").strftime("%Y-%m-%dT%H:%M:%SZ")
    organization = api_client.identity.create(
        type="Organization",
        name="My organization",
        alias=["my-organization"],
        description="A new organization.",
    )

    # Create the report
    report = api_client.report.create(
        name="My new report of my organization",
        description="A report wrote by my organization",
        published=date,
        report_types=["internal-report"],
        createdBy=organization["id"],
    )

    file = api_client.stix_domain_object.add_file(
        id=report["id"],
        file_name="./tests/integration/support_data/test.pdf",
    )

    connector = InternalInputConnector()
    work_id = api_client.stix_domain_object.file_ask_for_enrichment(file_id=file['data']['stixDomainObjectEdit']['importPush']['id'], connector_id=connector.base_config.id)

    t1 = threading.Thread(target=connector.start)
    t1.start()

    # api_client.work.wait_for_work_to_finish(work_id)
    time.sleep(3)

    assert "Sending container" in caplog.text, "No container sent"

    connector.stop()
    t1.join()
