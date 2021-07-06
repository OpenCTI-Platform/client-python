import pytest

from pycti import OpenCTIApiClient
from tests.modules.modules import (
    ThreatActorTest,
    ToolTest,
    VulnerabilityTest,
    SightingRelationshipTest,
    AttackPatternTest,
    CampaignTest,
    CourseOfActionTest,
    ExternalReferenceTest,
    IdentityTest,
    IncidentTest,
    InfrastructureTest,
    IndicatorTest,
    IntrusionSetTest,
    KillChainPhaseTest,
    LabelTest,
    LocationTest,
    MalwareTest,
    MarkingDefinitionTest,
    NoteTest,
    ObservedDataTest,
    OpinionTest,
    ReportTest,
    RelationshipTest,
    CyberObservableTest,
    CyberObservableRelationshipTest,
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
        "Attack-Pattern": AttackPatternTest(api_client),
        "Campaign": CampaignTest(api_client),
        "Course-Of-Action": CourseOfActionTest(api_client),
        "External-Reference": ExternalReferenceTest(api_client),
        "Identity": IdentityTest(api_client),
        "Incident": IncidentTest(api_client),
        "Infrastructure": InfrastructureTest(api_client),
        "Indicator": IndicatorTest(api_client),
        "IntrusionSet": IntrusionSetTest(api_client),
        "KillChainPhase": KillChainPhaseTest(api_client),
        "Label": LabelTest(api_client),
        "Location": LocationTest(api_client),
        "Malware": MalwareTest(api_client),
        "MarkingDefinition": MarkingDefinitionTest(api_client),
        "Note": NoteTest(api_client),
        "ObservedData": ObservedDataTest(api_client),
        "Opinion": OpinionTest(api_client),
        "Report": ReportTest(api_client),
        "Relationship": RelationshipTest(api_client),
        "CyberObservable": CyberObservableTest(api_client),
        "CyberObservableRelationship": CyberObservableRelationshipTest(api_client),
        # "StixDomainObject": TODO,
        # "StixObjectOrStixRelationship": TODO,
        "StixSightingRelationship": SightingRelationshipTest(api_client),
        "ThreatActor": ThreatActorTest(api_client),
        "Tool": ToolTest(api_client),
        "Vulnerability": VulnerabilityTest(api_client),
    }
