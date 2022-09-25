from pytest import fixture
from pycti.connector.new.tests.test_library import wait_for_test_to_finish
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
    yield connector
    connector.shutdown()
    connector.teardown()


def test_connector_run(connector_test_instance, api_client, caplog):
    connector_test_instance.run()
    bundle = wait_for_test_to_finish(connector_test_instance, api_client, caplog, {'last_run': None})
    connector_test_instance.verify(bundle)
