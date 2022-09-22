import pytest
from pytest_cases import fixture

from pycti import (
    OpenCTIApiClient,
    OpenCTIStix2Splitter,
)


@fixture(scope="session")
def api_client(pytestconfig):
    if pytestconfig.getoption("--opencti") and pytestconfig.getoption("--token"):
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