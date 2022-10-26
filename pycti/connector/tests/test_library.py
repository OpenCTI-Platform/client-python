import time
from typing import Dict


def wait_for_test_to_finish(connector_test_instance, old_state: Dict) -> str:
    connector_test_instance.initiate()

    finished = False
    error = ""
    while not finished:
        new_state = connector_test_instance.connector_instance.get_state()
        error = new_state.get("error", "")
        if error:
            finished = True

        if new_state.get("last_run", None) != old_state.get("last_run", None):
            finished = True

        time.sleep(0.5)

    return error
