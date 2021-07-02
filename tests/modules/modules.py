from stix2 import TLP_GREEN, TLP_WHITE
from tests.utils import get_incident_start_date, get_incident_end_date


class TestEntity:
    def __init__(self, api_client):
        self.api_client = api_client

    def setup(self):
        pass

    def teardown(self):
        pass

    def data(self):
        pass

    def ownclass(self):
        pass

    def baseclass(self):
        pass


class TestOrganization(TestEntity):
    def data(self):
        return {
            "type": "Organization",
            "name": "Testing Inc.",
            "description": "OpenCTI Test Org",
        }

    def baseclass(self):
        return self.api_client.stix_domain_object

    def ownclass(self):
        return self.api_client.identity


class TestIndicator(TestEntity):
    def setup(self):
        self.marking_definition_green = self.api_client.marking_definition.read(
            id=TLP_GREEN["id"]
        )
        self.marking_definition_white = self.api_client.marking_definition.read(
            id=TLP_WHITE["id"]
        )
        # Create the organization
        self.organization = self.api_client.identity.create(
            **TestOrganization(self.api_client).data()
        )

    def data(self):
        return {
            "type": "Indicator",
            "name": "C2 server of the new campaign",
            "description": "This is the C2 server of the campaign",
            "pattern_type": "stix",
            "pattern": "[domain-name:value = 'www.5z8.info' AND domain-name:resolves_to_refs[*].value = '198.51.100.1/32']",
            "x_opencti_main_observable_type": "IPv4-Addr",
            "confidence": 60,
            "x_opencti_score": 80,
            "x_opencti_detection": True,
            "valid_from": get_incident_start_date(),
            "valid_until": get_incident_end_date(),
            "created": get_incident_start_date(),
            "modified": get_incident_start_date(),
            "createdBy": self.organization["id"],
            "objectMarking": [
                self.marking_definition_green["id"],
                self.marking_definition_white["id"],
            ],
            "update": True,
            # TODO killchain phase
        }

    def teardown(self):
        self.api_client.stix_domain_object.delete(id=self.organization["id"])

    def ownclass(self):
        return self.api_client.indicator

    def baseclass(self):
        return self.api_client.stix_domain_object


class TestAttackPattern(TestEntity):
    def data(self):
        return {
            "type": "AttackPattern",
            "name": "Evil Pattern",
            "x_mitre_id": "T1999",
            "description": "Test Attack Pattern",
        }

    def baseclass(self):
        return self.api_client.stix_domain_object

    def ownclass(self):
        return self.api_client.attack_pattern
