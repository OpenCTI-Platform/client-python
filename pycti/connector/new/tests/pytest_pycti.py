from typing import List
import pytest
from _pytest.config.argparsing import Parser
from _pytest.config import Config
from _pytest.nodes import Item
from pytest import fixture, hookimpl
from pycti import (
    OpenCTIApiClient,
    OpenCTIStix2Splitter,
)
from pycti.connector.new.tests.test_class import RabbitMQ, DummyConnector


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--connectors", action="store_true", default=False, help="run connector tests"
    )
    parser.addoption("--opencti", action="store", help="OpenCTI URL")
    parser.addoption("--token", action="store", help="OpenCTI Token")
    parser.addoption(
        "--no_verify_ssl",
        action="store_true",
        default=False,
        help="Verify OpenCTI TLS certificate",
    )
    parser.addoption(
        "--drone",
        action="store_true",
        default=False,
        help="run connector tests in drone environment",
    )


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "connectors: mark connector tests to run")


@hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    if config.getoption("--connectors"):
        return
    skip_connectors = pytest.mark.skip(reason="need --connectors to run")
    for item in items:
        if "connectors" in item.keywords:
            item.add_marker(skip_connectors)


@fixture(scope="session")
def api_client(pytestconfig):
    if pytestconfig.getoption("--opencti", None) and pytestconfig.getoption(
        "--token", None
    ):
        url = pytestconfig.getoption("--opencti")
        token = pytestconfig.getoption("--token")
        verify_ssl = pytestconfig.getoption("--no_verify_ssl")
        return OpenCTIApiClient(url, token, ssl_verify=verify_ssl ^ True)
    elif pytestconfig.getoption("--drone"):
        return OpenCTIApiClient(
            "http://opencti:4000",
            "bfa014e0-e02e-4aa6-a42b-603b19dcf159",
            ssl_verify=False,
        )
    else:
        return OpenCTIApiClient(
            "https://demo.opencti.io",
            "7e663f91-d048-4a8b-bdfa-cdb55597942b",
            ssl_verify=True,
        )


@fixture(scope="function")
def rabbit_server(api_client):
    config = api_client.connector.register(DummyConnector())
    api_client.connector.unregister(config["id"])
    rabbit = RabbitMQ(
        config["config"]["connection"]["host"],
        config["config"]["connection"]["port"],
        config["config"]["connection"]["user"],
        config["config"]["connection"]["pass"],
    )
    rabbit.setup()
    yield rabbit
    rabbit.shutdown()


@fixture(scope="session")
def opencti_splitter():
    return OpenCTIStix2Splitter()
