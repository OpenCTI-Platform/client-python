import uuid

import pika.exceptions
import pytest
from pytest_cases import fixture, parametrize_with_cases

from pycti import OpenCTIApiClient, OpenCTIApiWork, OpenCTIConnector
from pycti.entities.opencti_marking_definition import MarkingDefinition
from pycti.utils.constants import DataSegregationMarking
from tests.cases.connectors import (
    ConnectorRegisteringMarkings,
    ConnectorRegisteringMarkingsTest,
    ExternalImportConnector,
    ExternalImportConnectorTest,
    InternalEnrichmentConnector,
    InternalEnrichmentConnectorTest,
    InternalImportConnector,
    InternalImportConnectorTest,
    SimpleConnectorTest,
)
from tests.utils import get_connector_id, get_new_work_id


@fixture
@parametrize_with_cases("connector", cases=SimpleConnectorTest)
def simple_connector(connector, api_connector, api_work):
    connector = OpenCTIConnector(**connector)
    api_connector.register(connector)
    yield connector
    # Unregistering twice just to make sure
    try:
        api_connector.unregister(connector.to_input()["input"]["id"])
    except ValueError:
        # Ignore "Can't find element to delete" error
        pass


@pytest.mark.skip
@pytest.mark.connectors
def test_register_simple_connector(simple_connector, api_connector, api_work):
    my_connector_id = simple_connector.to_input()["input"]["id"]

    test_connector = ""
    registered_connectors = api_connector.list()
    for registered_connector in registered_connectors:
        if registered_connector["id"] == my_connector_id:
            test_connector = registered_connector["id"]
            break

    assert (
        test_connector == my_connector_id
    ), f"No registered connector with id '{my_connector_id}' found"

    api_connector.unregister(test_connector)

    test_connector = ""
    registered_connectors = api_connector.list()
    for registered_connector in registered_connectors:
        if registered_connector["id"] == my_connector_id:
            test_connector = registered_connector["id"]
            break

    assert test_connector == "", "Connector is still registered"


@fixture
@parametrize_with_cases("data", cases=ExternalImportConnectorTest)
def external_import_connector_data(data, api_client, api_connector, api_work):
    connector = ExternalImportConnector(data["config"], api_client, data["data"])
    connector.run()
    yield data["data"]
    connector.stop()

    # Cleanup finished works
    works = api_work.get_connector_works(connector.helper.connector_id)
    for work in works:
        api_work.delete_work(work["id"])


@pytest.mark.skip
@pytest.mark.connectors
def test_external_import_connector(
    external_import_connector_data, api_client, api_connector, api_work
):
    connector_name = "TestExternalImport"
    connector_id = get_connector_id(connector_name, api_connector)
    assert connector_id != "", f"{connector_name} could not be found!"

    # Wait until new work is registered
    work_id = get_new_work_id(api_client, connector_id)
    # Wait for opencti to finish processing task
    api_work.wait_for_work_to_finish(work_id)

    status_msg = api_work.get_work(work_id)
    assert (
        status_msg["tracking"]["import_expected_number"] == 2
    ), f"Unexpected number of 'import_expected_number'. Expected 2, Actual {status_msg['tracking']['import_expected_number']}"
    assert (
        status_msg["tracking"]["import_processed_number"] == 2
    ), f"Unexpected number of 'import_processed_number'. Expected 2, Actual {status_msg['tracking']['import_processed_number']}"

    for elem in external_import_connector_data:
        sdo = api_client.stix_domain_object.read(
            filters={
                "mode": "and",
                "filters": [{"key": "name", "values": elem["name"]}],
                "filterGroups": [],
            }
        )
        if sdo is None:
            continue
        assert (
            sdo is not None
        ), f"Connector was unable to create {elem['type']} via the Bundle"
        assert (
            sdo["entity_type"] == elem["type"]
        ), f"A different {elem['type']} type was created"

        api_client.stix_domain_object.delete(id=sdo["id"])


@fixture
@parametrize_with_cases("data", cases=InternalEnrichmentConnectorTest)
def internal_enrichment_connector_data(data, api_client, api_connector, api_work):
    enrichment_connector = InternalEnrichmentConnector(
        data["config"], api_client, data["data"]
    )

    try:
        enrichment_connector.start()
    except pika.exceptions.AMQPConnectionError:
        enrichment_connector.stop()
        raise ValueError("Connector was not able to establish the connection to pika")

    observable = api_client.stix_cyber_observable.create(**data["data"])
    yield observable["id"]

    api_client.stix_cyber_observable.delete(id=observable["id"])
    enrichment_connector.stop()

    # Cleanup finished works
    works = api_work.get_connector_works(enrichment_connector.helper.connector_id)
    for work in works:
        api_work.delete_work(work["id"])


@pytest.mark.skip
@pytest.mark.connectors
def test_internal_enrichment_connector(
    internal_enrichment_connector_data, api_connector, api_work, api_client
):
    # Rename variable
    observable_id = internal_enrichment_connector_data
    observable = api_client.stix_cyber_observable.read(id=observable_id)
    assert (
        observable["x_opencti_score"] == 30
    ), f"Score of {observable['value']} is not 30. Instead {observable['x_opencti_score']}"

    connector_name = "SetScore100Enrichment"
    connector_id = get_connector_id(connector_name, api_connector)
    assert connector_id != "", f"{connector_name} could not be found!"

    work_id = api_client.stix_cyber_observable.ask_for_enrichment(
        id=observable_id, connector_id=connector_id
    )

    # Wait for enrichment to finish
    api_work.wait_for_work_to_finish(work_id)

    observable = api_client.stix_cyber_observable.read(id=observable_id)
    assert (
        observable["x_opencti_score"] == 100
    ), f"Score of {observable['value']} is not 100. Instead {observable['x_opencti_score']}"


@fixture
@parametrize_with_cases("data", cases=InternalImportConnectorTest)
def internal_import_connector_data(data, api_client, api_connector, api_work):
    import_connector = InternalImportConnector(
        data["config"], api_client, data["observable"]
    )
    import_connector.start()

    report = api_client.report.create(**data["report"])

    yield report["id"], data

    api_client.stix_domain_object.delete(id=report["id"])
    import_connector.stop()

    # Cleanup finished works
    works = api_work.get_connector_works(import_connector.helper.connector_id)
    for work in works:
        api_work.delete_work(work["id"])


@pytest.mark.skip
@pytest.mark.connectors
def test_internal_import_connector(
    internal_import_connector_data, api_connector, api_work, api_client
):
    # Rename variable
    report_id, data = internal_import_connector_data
    observable_data = data["observable"]
    file_data = data["import_file"]

    connector_name = "ParseFileTest"
    connector_id = get_connector_id(connector_name, api_connector)
    assert connector_id != "", f"{connector_name} could not be found!"

    api_client.stix_domain_object.add_file(
        id=report_id,
        file_name=file_data,
    )

    # Wait until new work is registered
    work_id = get_new_work_id(api_client, connector_id)
    # Wait for opencti to finish processing task
    api_work.wait_for_work_to_finish(work_id)

    status_msg = api_work.get_work(work_id)
    assert (
        status_msg["tracking"]["import_expected_number"] == 2
    ), f"Unexpected number of 'import_expected_number'. Expected 2, Actual {status_msg['tracking']['import_expected_number']}"
    assert (
        status_msg["tracking"]["import_processed_number"] == 2
    ), f"Unexpected number of 'import_processed_number'. Expected 2, Actual {status_msg['tracking']['import_processed_number']}"

    report = api_client.report.read(id=report_id)
    assert (
        len(report["objects"]) == 1
    ), f"Unexpected referenced objects to report. Expected: 1, Actual: {len(report['objects'])}"

    observable_id = report["objects"][0]["id"]
    observable = api_client.stix_cyber_observable.read(id=observable_id)
    observable_type = observable_data["simple_observable_key"].split(".")[0]
    assert (
        observable["entity_type"] == observable_type
    ), f"Unexpected Observable type, received {observable_type}"
    assert (
        observable["value"] == observable_data["simple_observable_value"]
    ), f"Unexpected Observable value, received {observable['value']}"

    api_client.stix_cyber_observable.delete(id=observable_id)


@fixture
@parametrize_with_cases("test_data", cases=ConnectorRegisteringMarkingsTest)
def connector_registering_marking_data(
    test_data,
    api_client: OpenCTIApiClient,
    api_connector: OpenCTIConnector,
    api_work: OpenCTIApiWork,
):
    """Test that a connector adds custom markings for access control.

    Note: we do NOT test whether OpenCTI correctly enforces access control using
    these markings, only that they are correctly associated to an object
    """

    connector_id = str(uuid.uuid4())

    for marking_type in [
        DataSegregationMarking.AUTHOR,
        DataSegregationMarking.CONNECTOR,
    ]:
        default_marking = marking_type.default()
        marking_definition_object = MarkingDefinition(api_client)
        marking = marking_definition_object.create(
            definition_type=default_marking["definition_type"],
            definition=default_marking["definition"],
            x_opencti_color=default_marking["x_opencti_color"],
        )
        print(f"Created Marking: {marking}")
        assert (
            marking != None
        ), f"Failed to add default marking for {marking_type} on test initialization"

    connector = ConnectorRegisteringMarkings(
        test_data["config"],
        api_client,
        test_data["data"],
        connector_id,
        test_data["add_markings"],
        test_data["add_markings_author"],
    )
    connector.run()
    info = {"connector_id": connector_id, "test_data": test_data["data"]}
    yield info
    connector.stop()


@pytest.mark.connectors
def test_connector_registers_marking(
    connector_registering_marking_data,
    api_client: OpenCTIApiClient,
    api_connector: OpenCTIConnector,
    api_work: OpenCTIApiWork,
):
    connector_name = "_".join(
        [
            "TestConnectorRegisteringMarkings",
            connector_registering_marking_data["connector_id"],
        ]
    )
    connector_id = get_connector_id(connector_name, api_connector)
    assert connector_id != "", f"{connector_name} could not be found!"

    # Wait until new work is registered
    work_id = get_new_work_id(api_client, connector_id)
    # Wait for opencti to finish processing task
    api_work.wait_for_work_to_finish(work_id)

    # Retrieve the results
    results = []  # tuples: test_object->octi_object
    markings_to_remove = set()
    for test_object in connector_registering_marking_data["test_data"]:
        octi_object = api_client.stix_domain_object.read(
            filters={
                "mode": "and",
                "filters": [
                    {"key": "standard_id", "values": test_object["standard_id"]}
                ],
                "filterGroups": [],
            }
        )

        results.append((test_object, octi_object))

        if octi_object != None:
            for marking in octi_object.get("objectMarking", []):
                markings_to_remove.add(marking["standard_id"])

    # Cleanup: remove the objects that were added
    for _, octi_object in results:
        if octi_object != None:
            api_client.stix.delete(id=octi_object["standard_id"])
    # Cleanup: remove the markings that were added, and the default ones
    for id in markings_to_remove:
        api_client.stix.delete(id=id)
    # Cleanup: remove the default markings that were added during the test
    for marking in [DataSegregationMarking.AUTHOR, DataSegregationMarking.CONNECTOR]:
        try:
            octi_marking_object = api_client.marking_definition.read(
                filters={
                    "mode": "and",
                    "filters": [
                        {
                            "key": "definition_type",
                            "values": marking["definition_type"],
                        },
                        {"key": "definition", "values": marking["definition"]},
                    ],
                    "filterGroups": [],
                }
            )
            id = octi_marking_object["standard_id"]
            api_client.stix.delete(id=id)
        except:
            # was already deleted in the step before
            pass

    # Verify the results
    for test_object, octi_object in results:
        assert (
            octi_object != None
        ), f"Following test object did not get ingested into OpenCTI: {test_object["name"]}"

        related_markings = []
        for marking in octi_object.get("objectMarking", []):
            # only test for markings related to custom permissions
            if marking["definition_type"].startswith(
                DataSegregationMarking.marking_prefix()
            ):
                related_markings.append(marking)

        # verify connector markings
        connector_markings = [
            marking
            for marking in related_markings
            if marking["definition_type"]
            == DataSegregationMarking.CONNECTOR.definition_type()
        ]
        if test_object["connector_marking_expected"]:
            assert (
                len(connector_markings) == 1
            ), f"There should be exactly 1 connector marking, but there are {len(connector_markings)} in entity named {octi_object["name"]}"

            connector_marking = connector_markings[0]

            if test_object["connector_marking_should_be_default"]:
                assert (
                    connector_marking["definition"]
                    == DataSegregationMarking.CONNECTOR.default()["definition"]
                ), f"Connector marking should be the default one, but instead it has definition: {connector_marking}"
            else:
                assert connector_marking["definition"].startswith(
                    connector_name
                ), f"Connector marking should start with {connector_name}, but it is instead {connector_marking["definition"]} for entity {octi_object["name"]}"

        else:
            assert (
                len(connector_markings) == 0
            ), f"There should be 0 connector markings, but there are {len(connector_markings)} in entity named {octi_object["name"]}"

        # verify author markings
        author_markings = [
            marking
            for marking in related_markings
            if marking["definition_type"]
            == DataSegregationMarking.AUTHOR.definition_type()
        ]
        if test_object["author_marking_expected"]:
            assert (
                len(author_markings) == 1
            ), f"There should be exactly 1 author marking, but there are {len(author_markings)} in entity named {octi_object["name"]}"

            author_marking = author_markings[0]

            if test_object["author_marking_should_be_default"]:
                assert (
                    author_marking["definition"]
                    == DataSegregationMarking.AUTHOR.default()["definition"]
                ), f"Author marking should be the default one, but instead it has definition: {author_marking["definition"]}"
            else:
                assert author_marking["definition"].startswith(
                    test_object["expected_author_name"]
                ), f"Author marking should start with {test_object["expected_author_name"]}, but it is instead {author_marking["definition"]} for entity {octi_object["name"]}"

        else:
            assert (
                len(author_markings) == 0
            ), f"There should be 0 author markings, but there are {len(author_markings)} in entity named {octi_object["name"]}"
