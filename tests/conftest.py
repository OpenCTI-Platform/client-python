from pytest_cases import fixture
from pycti import OpenCTIApiClient, OpenCTIApiConnector
from tests.modules.connectors import SimpleConnectorTest


@fixture(scope="session")
def api_client():
    return OpenCTIApiClient(
        "https://demo.opencti.io",
        "e43f4012-9fe2-4ece-bb3f-fe9572e5993b",
        ssl_verify=True,
    )


@fixture(scope="session")
def api_connector(api_client):
    return OpenCTIApiConnector(api_client)


@fixture
def simple_connector() -> SimpleConnectorTest:
    return SimpleConnectorTest()
