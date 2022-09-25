import time
import base64
import json
import time
from stix2 import Bundle
from pycti.connector.new.libs.opencti_schema import WorkerMessage


def wait_for_test_to_finish(connector_test_instance, api_client, caplog, old_state) -> Bundle:
    work_id = connector_test_instance.initiate()

    finished = False
    while not finished:
        new_state = connector_test_instance.connector_instance.get_state()
        if new_state.get('last_run', None) != old_state.get('last_run', None):
            finished = True

        time.sleep(0.5)

    container = ""
    for msg in caplog.records:
        if "Sending container" in msg.msg:
            container = msg.msg.split(":", 1)[-1]

    assert container != "", "No container sent"

    worker_message = WorkerMessage(**json.loads(container))
    bundle = Bundle(
        **json.loads(base64.b64decode(worker_message.content)), allow_custom=True
    )

    return bundle
