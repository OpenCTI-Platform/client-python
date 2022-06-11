import pytest
from pytest_cases import fixture
from pycti import (
    OpenCTIApiClient,
    OpenCTIStix2Splitter,
)


@fixture(scope="session")
def api_client():
    return OpenCTIApiClient(
        "https://demo.opencti.io",
        "d1b42111-a7fb-4830-846a-6a91c16b0084",
        ssl_verify=True,
    )

@fixture(scope="session")
def schedule_server():
    return "http://localhost:5000"

@fixture(scope="session")
def opencti_splitter():
    return OpenCTIStix2Splitter()


@fixture(scope="session")
def httpserver_listen_address():
    return "localhost", 8888


def pytest_addoption(parser):
    parser.addoption(
        "--connectors", action="store_true", default=False, help="run connector tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "connectors: mark connector tests to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--connectors"):
        return
    skip_connectors = pytest.mark.skip(reason="need --connectors to run")
    for item in items:
        if "connectors" in item.keywords:
            item.add_marker(skip_connectors)
