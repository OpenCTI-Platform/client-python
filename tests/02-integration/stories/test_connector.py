import os
import time
import pika.exceptions
from pytest_cases import parametrize_with_cases
from pycti import OpenCTIConnector
from pycti.utils.constants import IdentityTypes
from tests.modules.connectors import ExternalEnrichmentConnector, SimpleConnectorTest


@parametrize_with_cases("simple_connector", cases=SimpleConnectorTest)
def test_register_simple_connector(api_connector, simple_connector):
    connector = OpenCTIConnector(**simple_connector)
    api_connector.register(connector)
    my_connector_id = connector.to_input()["input"]["id"]

    test_connector = ""
    registered_connectors = api_connector.list()
    for registered_connector in registered_connectors:
        if registered_connector["id"] == my_connector_id:
            test_connector = registered_connector["id"]
            break

    assert (
        test_connector == simple_connector["connector_id"]
    ), f"No registered connector with id '{simple_connector['connector_id']}' found"

    api_connector.unregister(test_connector)

    test_connector = ""
    registered_connectors = api_connector.list()
    for registered_connector in registered_connectors:
        if registered_connector["id"] == my_connector_id:
            test_connector = registered_connector["id"]
            break

    assert test_connector == "", "Connector is still registered"


def test_external_enrichment_connector(api_connector, api_client):
    # set OPENCTI settings from fixture
    os.environ["OPENCTI_URL"] = api_client.api_url
    os.environ["OPENCTI_TOKEN"] = api_client.api_token
    os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)

    config_file_path = "tests/data/connector_config.yml"
    data = {
        "api": {
            "type": IdentityTypes.ORGANIZATION.value,
            "name": "Testing aaaaaa",
            "description": "OpenCTI Test Org",
        },
        "bundle": {
            "type": "Vulnerability",
            "name": "CVE-1980-1234",
            "description": "evil evil evil",
        },
    }

    connector = ExternalEnrichmentConnector(config_file_path, api_client, data)
    try:
        connector.run()
    except pika.exceptions.AMQPConnectionError:
        connector.stop()
        raise ValueError("Connector was not able to establish the connection to pika")

    # Find identity
    identity = api_client.identity.read(
        filters=[{"key": "name", "values": data["api"]["name"]}]
    )
    assert identity is not None, "Connector was unable to create Identity via the API"
    assert (
        identity["entity_type"] == data["api"]["type"]
    ), "A different identity type was created"

    # Find vulnerability
    # Sleep timer to wait for bundle import finishing up
    # TODO find a better solution than a stupid sleep
    time.sleep(10)

    vulnerability = api_client.vulnerability.read(
        filters=[{"key": "name", "values": data["bundle"]["name"]}]
    )
    assert (
        vulnerability is not None
    ), "Connector was unable to create Vulnerability via bundle import"
    assert (
        vulnerability["entity_type"] == data["bundle"]["type"]
    ), "A different vulnerability type was created"

    api_client.stix_domain_object.delete(id=identity["id"])
    api_client.stix_domain_object.delete(id=vulnerability["id"])
