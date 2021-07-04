from typing import Dict
import pytest
from pycti import OpenCTIApiClient
from tests.modules.modules import (
    TestIndicator,
    TestIdentity,
    TestAttackPattern,
    TestNote,
    TestCourseOfAction,
    TestExternalReference,
    TestCampaign,
    TestIncident,
    TestInfrastructure,
    TestLocation,
    TestLabel,
    TestKillChainPhase,
    TestIntrusionSet,
    TestMalware,
    TestMarkingDefinition,
    TestObservedData,
)


# def pytest_addoption(parser):
#     parser.addoption(
#         "--online",
#         action="store_true",
#         default=False,
#         help="run tests on-line with OpenCTI demo instance",
#     )


@pytest.fixture
def api_client(request):
    # live_test = request.config.getoption("online")
    # if live_test:
    return OpenCTIApiClient(
        "https://demo.opencti.io",
        "681b01f9-542d-4c8c-be0c-b6c850b087c8",
        ssl_verify=True,
    )


@pytest.fixture
def fruit_bowl(api_client):
    return {
        # SDOs which don't create any other SDOs
        "Identity": TestIdentity(api_client),
        "Attack-Pattern": TestAttackPattern(api_client),
        "Campaign": TestCampaign(api_client),
        # TODO note update creates a new ID
        "Note": TestNote(api_client),
        "Course-Of-Action": TestCourseOfAction(api_client),
        "External-Reference": TestExternalReference(api_client),
        "Incident": TestIncident(api_client),
        "Infrastructure": TestInfrastructure(api_client),
        "Indicator": TestIndicator(api_client),
        "IntrusionSet": TestIntrusionSet(api_client),
        "KillChainPhase": TestKillChainPhase(api_client),
        "Label": TestLabel(api_client),
        "Location": TestLocation(api_client),
        "Malware": TestMalware(api_client),
        "MarkingDefinition": TestMarkingDefinition(api_client),
        "ObservedData": TestObservedData(api_client)
        # "Stix-Domain-Object": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.stix_domain_object,
        # "Campaign": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.campaign,
        # },
        # "Note": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.note,
        # },
        # "Observed-Data": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.observed_data,
        # },
        # "Opinion": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.opinion,
        # },
        # "Report": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.report,
        # },
        # "Course-Of-Action": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.course_of_action,
        # },
        # "Identity": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.identity,
        # },
        # "Infrastructure": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.infrastructure,
        # },
        # "Intrusion-Set": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.intrusion_set,
        # },
        # "Location": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.location,
        # },
        # "Malware": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.malware,
        # },
        # "Threat-Actor": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.threat_actor,
        # },
        # "Tool": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.tool,
        # },
        # "Vulnerability": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.vulnerability,
        # },
        # "Incident": {
        #     "data": "",
        #     "base_class": api_client.stix_domain_object,
        #     "class": api_client.incident,
        # },
        # "Stix-Cyber-Observable": {
        #     "data": "",
        #     "base_class": api_client.stix_cyber_observable,
        #     "class": api_client.stix_cyber_observable,
        # },
    }


def organization() -> Dict:
    return {
        "type": "Organization",
        "name": "Testing Inc.",
        "description": "OpenCTI Test Org",
    }
