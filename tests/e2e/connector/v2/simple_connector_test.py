import json
import time
from typing import List, Optional

import requests
from time import sleep

from pycti.connector.v2.connectors.connector import Connector
from pycti.connector.v2.libs.orchestrator_schemas import (
    WorkflowCreate,
    RunCreate,
    ConfigCreate,
    Config,
    Workflow,
    Run,
    JobStatus,
    State,
    Result,
)
from .stix_ingester import StixWorker, TestExternalImport


def test_connector_setup_and_heartbeat(schedule_server, monkeypatch, caplog):
    monkeypatch.setenv("scheduler", schedule_server)
    connector = StixWorker()
    sleep(5 + 1)  # 5 = heartbeat delay and 1 to avoid race condition
    assert "Successful heartbeat OK" in caplog.text, "No heartbeat detected"
    connector.stop()
    assert "Successful heartbeat removal" in caplog.text, "Heartbeat removal failed"


def test_connector_heartbeat_service(schedule_server, monkeypatch):
    monkeypatch.setenv("scheduler", schedule_server)
    # TODO continue here
    connector = StixWorker()
    connector_instance = connector.connector_instance
    response = requests.post(
        url=f"{schedule_server}/workflow/",
        json={"connector_instance": connector_instance},
    )
    sleep(20)
    connector.stop()


def get_element(
    job_status_list: List[JobStatus], config_id: str
) -> Optional[JobStatus]:
    for job_status in job_status_list:
        if job_status.id == config_id:
            return job_status

    return None


def test_connector_workflow(schedule_server, monkeypatch):
    monkeypatch.setenv("scheduler", schedule_server)
    stix_worker = StixWorker()
    stix_worker_config = ConfigCreate(
        connector_id=stix_worker.connector.id,
        name="StixWorker Config2",
        config=StixWorker.StixRunConfig(token="18bd74e5-404c-4216-ac74-23de6249d690"),
    )
    response = requests.post(
        f"{schedule_server}/config/", json=stix_worker_config.dict()
    )
    assert response.status_code == 201
    stix_config = Config(**json.loads(response.text))
    external_import = TestExternalImport()
    external_import_config = ConfigCreate(
        connector_id=external_import.connector.id,
        name="EI Import 192.168.14.1",
        config=TestExternalImport.TestExternalImportRunConfig(ip="192.168.14.1"),
    )
    response = requests.post(
        f"{schedule_server}/config/", json=external_import_config.dict()
    )
    ei_config = Config(**json.loads(response.text))
    job_order = [
        ei_config.id,
        stix_config.id,
    ]
    workflow_create = WorkflowCreate(
        name="Test Workflow",
        jobs=job_order,
        execution_type="triggered",
        execution_args="",
        token="123441",
    )
    print(workflow_create.json())
    response = requests.post(
        f"{schedule_server}/workflow/", json=workflow_create.dict()
    )
    workflow = Workflow(**json.loads(response.text))
    run_create = RunCreate(
        workflow_id=workflow.id,
        work_id="",
        applicant_id="",
        arguments="{}",
    )
    response = requests.post(
        f"{schedule_server}/workflow/{workflow.id}/run", json=run_create.dict()
    )
    print(response.text)
    assert response.status_code == 201
    assert "message" not in json.loads(response.text)
    run = Run(**json.loads(response.text))

    finished = False
    while not finished:
        response = requests.get(f"{schedule_server}/run/{run.id}")
        assert response.status_code == 200
        run = Run(**json.loads(response.text))
        for job in job_order:
            job_status = get_element(run.job_status, job)
            print(f"{job} - {job_status}")
            assert job_status is not None

            status = False
            if job_status.status == State.finished:
                assert job_status.result == Result.success
                status = True

        if run.status == State.finished:
            assert run.result == Result.success
            finished = True
        else:
            time.sleep(0.5)

    print("Finished")
    # verify created value
    stix_worker.stop()
    external_import.stop()
