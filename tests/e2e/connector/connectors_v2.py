from pytest import fixture
from pycti.connector.new.tests.test_library import test_connector_run # pylint: disable=unused-import

from tests.cases.external_input_connectors import ExternalInputTest
from tests.cases.internal_enrichment_connectors import (
    InternalEnrichmentTest,
)
from tests.cases.internal_file_input_connectors import (
    InternalFileInputTest,
)

CONNECTORS = [InternalFileInputTest, ExternalInputTest, InternalEnrichmentTest]

@fixture(params=CONNECTORS)
def connector_test_instance(request, api_client, monkeypatch):
    connector = request.param(api_client)
    connector.setup(monkeypatch)
    connector.run()
    yield connector
    connector.shutdown()
    connector.teardown()