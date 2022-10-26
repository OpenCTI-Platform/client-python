import base64
import json

from pytest import fixture, mark
from stix2 import Bundle

from pycti.connector.libs.opencti_schema import WorkerMessage
from pycti.connector.tests.test_library import wait_for_test_to_finish
from tests.cases.external_input_connectors import ExternalInputTest
from tests.cases.internal_enrichment_connectors import (
    InternalEnrichmentTest,
    InternalEnrichmentTest_TLP_Invalid,
)
from tests.cases.internal_file_input_connectors import (
    InternalFileInputTest,
    InternalFileInputWorkflowTest,
)
from tests.cases.worker_connector import WorkerTest

CONNECTORS = [
    InternalFileInputTest,
    ExternalInputTest,
    InternalEnrichmentTest,
    InternalEnrichmentTest_TLP_Invalid,
]
WORKFLOW_CONNECTORS = [InternalFileInputWorkflowTest]


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

    expected_error = connector_test_instance.get_expected_exception()
    if expected_error == "":
        assert error_msg == expected_error, f"Error during execution: {error_msg}"

        messages = rabbit_server.get_messages()
        for msg in messages:
            worker_message = WorkerMessage(**json.loads(msg))
            bundle = Bundle(
                **json.loads(base64.b64decode(worker_message.content)),
                allow_custom=True,
            )
            connector_test_instance.verify(bundle)

    else:
        assert (
            expected_error in error_msg
        ), f"Expected exception did not match occurred exception ({expected_error}) vs ({error_msg})"


@fixture(params=WORKFLOW_CONNECTORS)
def connector_test_workflow(request, api_client, monkeypatch):
    connector = request.param(api_client)
    connector.setup(monkeypatch)

    worker = WorkerTest(api_client)
    worker.setup(monkeypatch)

    yield connector, worker

    worker.shutdown()

    connector.shutdown()
    connector.teardown()


@mark.connectors
def test_connector_workflow_run(connector_test_workflow, api_client):
    connector, worker = connector_test_workflow

    connector.run()
    worker.run()

    error_msg = wait_for_test_to_finish(connector, {"last_run": None})
    work_ids = api_client.work.get_connector_works(
        connector.connector_instance.base_config.id
    )
    assert len(work_ids) > 0, f"Didn't get works for connector"

    work_id = work_ids[0]["id"]
    finished = False
    while not finished:
        work_info = api_client.work.get_work(work_id)
        if (
            work_info["tracking"]["import_expected_number"]
            == work_info["tracking"]["import_processed_number"]
        ):
            finished = True

    expected_error = connector.get_expected_exception()
    if expected_error == "":
        assert error_msg == expected_error, f"Error during execution: {error_msg}"

        connector.verify_imported()

    else:
        assert (
            expected_error in error_msg
        ), f"Expected exception did not match occurred exception ({expected_error}) vs ({error_msg})"
