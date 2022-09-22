from pycti.connector.new.tests.conftest import *


def pytest_addoption(parser):
    parser.addoption(
        "--connectors", action="store_true", default=False, help="run connector tests"
    )
    parser.addoption("--opencti", action="store", help="OpenCTI URL")
    parser.addoption("--token", action="store", help="OpenCTI Token")
    parser.addoption("--no_verify_ssl", action="store_true", default=False, help="Verify OpenCTI TLS certificate")


def pytest_configure(config):
    config.addinivalue_line("markers", "connectors: mark connector tests to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--connectors"):
        return
    skip_connectors = pytest.mark.skip(reason="need --connectors to run")
    for item in items:
        if "connectors" in item.keywords:
            item.add_marker(skip_connectors)
