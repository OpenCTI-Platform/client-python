from pytest_cases import fixture

from pycti import OpenCTIApiClient, OpenCTIApiConnector
from tests.modules.connectors import SimpleConnectorTest
from tests.modules.modules import (
    ThreatActorTest,
    ToolTest,
    VulnerabilityTest,
    StixSightingRelationshipTest,
    AttackPatternTest,
    CampaignTest,
    CourseOfActionTest,
    ExternalReferenceTest,
    IdentityTest,
    InfrastructureTest,
    IndicatorTest,
    IntrusionSetTest,
    KillChainPhaseTest,
    LabelTest,
    MalwareTest,
    MarkingDefinitionTest,
    NoteTest,
    ObservedDataTest,
    OpinionTest,
    ReportTest,
    StixCoreRelationshipTest,
    StixCyberObservableTest,
)


@fixture(scope="session")
def api_client():
    return OpenCTIApiClient(
        "https://demo.opencti.io",
        "e43f4012-9fe2-4ece-bb3f-fe9572e5993b",
        ssl_verify=True,
    )


@fixture
def api_connector(api_client):
    return OpenCTIApiConnector(api_client)


@fixture
def simple_connector() -> SimpleConnectorTest:
    return SimpleConnectorTest()


class EntityTestCases:
    @staticmethod
    def case_attack_pattern(api_client):
        return AttackPatternTest(api_client)

    @staticmethod
    def case_campaign(api_client):
        return CampaignTest(api_client)

    @staticmethod
    def case_course_of_action(api_client):
        return CourseOfActionTest(api_client)

    @staticmethod
    def case_external_reference(api_client):
        return ExternalReferenceTest(api_client)

    @staticmethod
    def case_identity(api_client):
        return IdentityTest(api_client)

    @staticmethod
    def case_infrastructure(api_client):
        return InfrastructureTest(api_client)

    @staticmethod
    def case_indicator(api_client):
        return IndicatorTest(api_client)

    @staticmethod
    def case_intrusion_set(api_client):
        return IntrusionSetTest(api_client)

    @staticmethod
    def case_kill_chain_phase(api_client):
        return KillChainPhaseTest(api_client)

    @staticmethod
    def case_label(api_client):
        return LabelTest(api_client)

    @staticmethod
    def case_malware(api_client):
        return MalwareTest(api_client)

    @staticmethod
    def case_marking_definition(api_client):
        return MarkingDefinitionTest(api_client)

    @staticmethod
    def case_note(api_client):
        return NoteTest(api_client)

    @staticmethod
    def case_observed_data(api_client):
        return ObservedDataTest(api_client)

    @staticmethod
    def case_opinion(api_client):
        return OpinionTest(api_client)

    @staticmethod
    def case_report(api_client):
        return ReportTest(api_client)

    @staticmethod
    def case_relationship(api_client):
        return StixCoreRelationshipTest(api_client)

    @staticmethod
    def case_stix_cyber_observable(api_client):
        return StixCyberObservableTest(api_client)

    @staticmethod
    def case_stix_sighting_relationship(api_client):
        return StixSightingRelationshipTest(api_client)

    @staticmethod
    def case_threat_actor(api_client):
        return ThreatActorTest(api_client)

    @staticmethod
    def case_tool(api_client):
        return ToolTest(api_client)

    @staticmethod
    def case_vulnerability(api_client):
        return VulnerabilityTest(api_client)
