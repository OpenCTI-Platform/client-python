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


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--connectors", action="store_true", default=False, help="run connector tests"
    )
    parser.addoption("--opencti", action="store", help="OpenCTI URL")
    parser.addoption("--token", action="store", help="OpenCTI Token")
    parser.addoption("--no_verify_ssl", action="store_true", default=False, help="Verify OpenCTI TLS certificate")


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
    if pytestconfig.getoption("--opencti", None) and pytestconfig.getoption("--token", None):
        url = pytestconfig.getoption("--opencti")
        token = pytestconfig.getoption("--token")
        verify_ssl = pytestconfig.getoption("--no_verify_ssl")
        return OpenCTIApiClient(
            url,
            token,
            ssl_verify=verify_ssl ^ True
        )
    else:
        return OpenCTIApiClient(
            "https://demo.opencti.io",
            "7e663f91-d048-4a8b-bdfa-cdb55597942b",
            ssl_verify=True,
        )


@fixture(scope="session")
def opencti_splitter():
    return OpenCTIStix2Splitter()
