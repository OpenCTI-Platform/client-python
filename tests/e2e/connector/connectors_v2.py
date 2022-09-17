import base64
import json
import time
from stix2 import Bundle

# from pytest_cases import fixture, parametrize_with_cases
# import pytest
from pytest import param, fixture
from pycti.connector.new.libs.opencti_schema import WorkerMessage
from tests.cases.external_input_connectors import ExternalInputTest
from tests.cases.internal_enrichment_connectors import (
    InternalEnrichmentTest,
)
from tests.cases.internal_file_input_connectors import (
    InternalFileInputTest,
)


@fixture(params=[InternalFileInputTest, ExternalInputTest, InternalEnrichmentTest])
def connector_test_instance(request, api_client, monkeypatch):
    connector = request.param(api_client)
    connector.setup(monkeypatch)
    connector.run()
    yield connector
    connector.shutdown()
    connector.teardown()


def test_connector_run(connector_test_instance, api_client, caplog):
    work_id = connector_test_instance.initiate()

    if not work_id:
        connector_works = api_client.work.get_connector_works(connector_test_instance.connector_instance.base_config.id)
        if len(connector_works) > 0:
            work_id = connector_works[0]['id']  # .split("_", 1)[-1]

    if work_id:
        api_client.work.wait_for_work_to_finish(work_id)
    else:
        time.sleep(3)

    container = ""
    for msg in caplog.records:
        if "Sending container" in msg.msg:
            container = msg.msg.split(":", 1)[-1]

    assert container != "", "No container sent"

    worker_message = WorkerMessage(**json.loads(container))
    bundle = Bundle(
        **json.loads(base64.b64decode(worker_message.content)), allow_custom=True
    )
    connector_test_instance.verify(bundle)
#
#
#
# @fixture(params=[ExternalInputTest])
# def external_input_connector(request, api_client, monkeypatch):
#     connector = request.param(api_client)
#     connector.setup(monkeypatch)
#     connector.run()
#     yield connector
#     connector.shutdown()
#     connector.teardown()
#
#
# def test_external_input_run(external_input_connector, api_client, caplog):
#     time.sleep(2)
#
#     container = ""
#     for msg in caplog.records:
#         if "Sending container" in msg.msg:
#             container = msg.msg.split(":", 1)[-1]
#
#     assert container != "", "No container sent"
#
#     worker_message = WorkerMessage(**json.loads(container))
#     bundle = Bundle(
#         **json.loads(base64.b64decode(worker_message.content)), allow_custom=True
#     )
#     external_input_connector.verify(bundle)
#
#
#
# @fixture(params=[InternalEnrichmentTest])
# def internal_enrichment_connector(request, api_client, monkeypatch):
#     connector = request.param(api_client)
#     connector.setup(monkeypatch)
#     connector.run()
#     yield connector
#     connector.teardown()
#     connector.shutdown()
#
#
# def test_internal_enrichment_run(internal_enrichment_connector, api_client, caplog):
#     work_id = api_client.stix_cyber_observable.ask_for_enrichment(
#         id=internal_enrichment_connector.ipv4["id"],
#         connector_id=internal_enrichment_connector.connector.base_config.id,
#     )
#
#     # WTF??
#     # FAILED [ 66%]Connector works {'data': {'works': {'edges': [{'node': {'id': 'work_099ea3e5-01a2-460a-a17d-50ff45cce844_2022-09-07T13:12:18.131Z', 'name': 'Manual enrichment', 'user': {'name': 'admin'}, 'timestamp': '2022-09-07T13:12:18.131Z', 'status': 'wait', 'event_source_id': '8d89bfec-2c23-482e-8334-66c990c92ffc', 'received_time': None, 'processed_time': None, 'completed_time': None, 'tracking': {'import_expected_number': None, 'import_processed_number': None}, 'messages': [], 'errors': []}}]}}}
#     # 2022-09-07 15:12:18,259 - PikaBroker - INFO - Received b'{"internal":{"work_id":"work_099ea3e5-01a2-460a-a17d-50ff45cce844_2022-09-07T13:12:18.131Z","applicant_id":"88ec0c6a-13ce-5e39-b486-354fe4a7084f"},"event":{"entity_id":"8d89bfec-2c23-482e-8334-66c990c92ffc"}}'
#
#     #connector_works = api_client.work.get_connector_works(internal_enrichment_connector.connector.base_config.id)
#     #assert len(connector_works) > 0, "No works registered"
#     #work_id = connector_works[0]['id'] #['id'].split("_", 1)[-1]
#     print(f"Work id {work_id}")
#     api_client.work.wait_for_work_to_finish(work_id)
#
#     container = ""
#     for msg in caplog.records:
#         if "Sending container" in msg.msg:
#             container = msg.msg.split(":", 1)[-1]
#
#     assert container != "", "No container sent"
#
#     worker_message = WorkerMessage(**json.loads(container))
#     bundle = Bundle(
#         **json.loads(base64.b64decode(worker_message.content)), allow_custom=True
#     )
#     internal_enrichment_connector.verify(bundle)
