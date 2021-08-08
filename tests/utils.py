import datetime
import time
from dateutil.parser import parse
from pycti import OpenCTIApiConnector, OpenCTIApiClient, OpenCTIApiWork


def get_incident_start_date():
    return (
        parse("2019-12-01")
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(sep="T", timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def get_incident_end_date():
    return (
        parse("2021-12-01")
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(sep="T", timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def read_marking(api_client: OpenCTIApiClient, tlp_id: int):
    return api_client.marking_definition.read(id=tlp_id)


def get_connector_id(connector_name: str, api_connector: OpenCTIApiConnector) -> str:
    connector_list = api_connector.list()
    connector_id = ""
    for connector in connector_list:
        if connector["name"] == connector_name:
            connector_id = connector["id"]

    return connector_id


def get_new_work_id(api_client: OpenCTIApiClient, connector_id: str) -> str:
    worker = OpenCTIApiWork(api_client)
    new_works = worker.get_connector_works(connector_id)
    cnt = 0
    while len(new_works) == 0:
        time.sleep(1)
        # wait 20 seconds for new work to be registered
        cnt += 1
        if cnt > 20:
            assert (
                cnt != cnt
            ), "Connector hasn't registered new work yet. Elapsed time 20s"

        assert (
            len(new_works) == 1
        ), f"Too many jobs were created. Expected 1, Actual: {len(new_works)}"
    return new_works[0]["id"]
