import os
import threading
import uuid

import pytest
import time
from pytest_cases import parametrize_with_cases, fixture

from tests.e2e.support_cases.connectors_v2 import (
    TestExternalImportConnectors,
    TestInternalImportFileConnectors,
)
from tests.utils import get_new_work_id


@fixture
@parametrize_with_cases("connector", cases=TestExternalImportConnectors)
def external_import_connector(api_client, connector):
    os.environ["OPENCTI_URL"] = api_client.opencti_url
    os.environ["OPENCTI_TOKEN"] = api_client.api_token
    os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)
    os.environ["CONNECTOR_JSON_LOGGING"] = "false"

    connector_id = str(uuid.uuid4())
    connector_name = "TestExternalImportConnector"

    os.environ["CONNECTOR_ID"] = connector_id
    os.environ["CONNECTOR_NAME"] = connector_name
    os.environ["CONNECTOR_CONFIDENCE_LEVEL"] = "100"
    os.environ["CONNECTOR_LOG_LEVEL"] = "INFO"
    os.environ[
        "APP_URL"
    ] = "https://github.com/oasis-open/cti-stix-common-objects/raw/main/objects/marking-definition/marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf.json"

    connector = connector()
    connector.test_setup(api_client)

    # wait for worker to register thread
    time.sleep(60)

    x = threading.Thread(target=connector.process_broker_message, daemon=True)
    x.start()

    work_id = get_new_work_id(api_client, connector_id)
    api_client.work.wait_for_work_to_finish(work_id)

    yield connector

    # Cleanup finished works
    works = api_client.work.get_connector_works(connector.base_config.connector.id)
    for work in works:
        api_client.work.delete_work(work["id"])

    connector.stop()
    connector.test_teardown(api_client)


@pytest.mark.connectors
def test_export_import_verify(external_import_connector, api_client):
    marking_definition = api_client.marking_definition.read(
        id="marking-definition--62fd3f9b-15f3-4ebc-802c-91fce9536bcf"
    )
    assert marking_definition, "Marking Definition was not found"


@fixture
@parametrize_with_cases("connector", cases=TestInternalImportFileConnectors)
def import_file_connector(api_client, connector):
    os.environ["OPENCTI_URL"] = api_client.opencti_url
    os.environ["OPENCTI_TOKEN"] = api_client.api_token
    os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)
    os.environ["CONNECTOR_JSON_LOGGING"] = "false"

    connector_id = str(uuid.uuid4())
    connector_name = "TestStixImportConnector"

    os.environ["CONNECTOR_ID"] = connector_id
    os.environ["CONNECTOR_NAME"] = connector_name
    os.environ["CONNECTOR_CONFIDENCE_LEVEL"] = "100"
    os.environ["CONNECTOR_LOG_LEVEL"] = "INFO"
    os.environ["CONNECTOR_SCOPE"] = "text/plain,text/xml,application/json"
    os.environ["CONNECTOR_AUTO"] = "true"
    os.environ["CONNECTOR_EXTERNAL_IDENTITY"] = "123456789"

    connector = connector()
    x = threading.Thread(target=connector.process_broker_message, daemon=True)
    x.start()

    # wait for worker to register thread
    time.sleep(60)

    connector.test_setup(api_client)

    work_id = get_new_work_id(api_client, connector_id)
    api_client.work.wait_for_work_to_finish(work_id)

    yield connector

    connector.stop()
    x.join()
    connector.test_teardown(api_client)

    # Cleanup finished works
    works = api_client.work.get_connector_works(connector.base_config.connector.id)
    for work in works:
        api_client.work.delete_work(work["id"])


@pytest.mark.connectors
def test_import_file_verify(api_client, import_file_connector):
    location = api_client.location.read(
        id="location--011a9d8e-75eb-475a-a861-6998e9968287"
    )
    assert location, "Location was not found"
