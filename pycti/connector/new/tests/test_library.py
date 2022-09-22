import base64
import json
import time
from stix2 import Bundle
from pycti.connector.new.libs.opencti_schema import WorkerMessage


# CONNECTORS = []
#
#
# @fixture(params=CONNECTORS)
# def connector_test_instance(request, api_client, monkeypatch):
#     connector = request.param(api_client)
#     connector.setup(monkeypatch)
#     connector.run()
#     yield connector
#     connector.shutdown()
#     connector.teardown()
# #
#


def test_connector_run(connector_test_instance, api_client, caplog):
    work_id = connector_test_instance.initiate()

    if not work_id:
        connector_works = api_client.work.get_connector_works(connector_test_instance.connector_instance.base_config.id)
        if len(connector_works) > 0:
            work_id = connector_works[0]['id']

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
