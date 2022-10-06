import base64
import json

from pytest import fixture, mark
from pycti.connector.new.tests.test_library import wait_for_test_to_finish
from tests.cases.external_input_connectors import ExternalInputTest
from tests.cases.internal_enrichment_connectors import (
    InternalEnrichmentTest,
)
from tests.cases.internal_file_input_connectors import (
    InternalFileInputTest,
)
from stix2 import Bundle
from pycti.connector.new.libs.opencti_schema import WorkerMessage

CONNECTORS = [InternalFileInputTest, ExternalInputTest, InternalEnrichmentTest]


@fixture(params=CONNECTORS)
def connector_test_instance(request, api_client, monkeypatch):
    connector = request.param(api_client)
    connector.setup(monkeypatch)
    yield connector
    connector.shutdown()
    connector.teardown()


@mark.connectors
def test_connector_run(connector_test_instance, rabbit_server):
    connector_test_instance.run()
    rabbit_server.run(
        connector_test_instance.connector_instance.base_config.name.lower()
    )

    error_msg = wait_for_test_to_finish(connector_test_instance, {"last_run": None})

    assert error_msg == "", f"Error during execution: {error_msg}"

    messages = rabbit_server.get_messages()
    for msg in messages:
        worker_message = WorkerMessage(**json.loads(msg))
        bundle = Bundle(
            **json.loads(base64.b64decode(worker_message.content)), allow_custom=True
        )
        connector_test_instance.verify(bundle)
