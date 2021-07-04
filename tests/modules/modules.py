from typing import List, Dict

from stix2 import TLP_GREEN, TLP_WHITE

from pycti import OpenCTIStix2Utils
from pycti.utils.constants import LocationTypes, IdentityTypes
from tests.utils import get_incident_start_date, get_incident_end_date


class TestEntity:
    def __init__(self, api_client):
        self.api_client = api_client

    def setup(self):
        pass

    def teardown(self):
        pass

    def data(self) -> List[Dict]:
        pass

    def ownclass(self):
        pass

    def baseclass(self):
        return self.api_client.stix_domain_object


class TestIdentity(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": IdentityTypes.ORGANIZATION.value,
                "name": "Testing Inc.",
                "description": "OpenCTI Test Org",
            },
            {
                "type": IdentityTypes.INDIVIDUAL.value,
                "name": "Jane Smith",
                "description": "Mrs awesome",
            },
            {
                "type": IdentityTypes.SECTOR.value,
                "name": "Energetic",
                "description": "The energetic sector",
            },
        ]

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
            **TestIdentity(self.api_client).data()[0]
        )

    def data(self) -> List[Dict]:
        return [
            {
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
        ]

    def teardown(self):
        self.api_client.stix_domain_object.delete(id=self.organization["id"])

    def ownclass(self):
        return self.api_client.indicator


class TestAttackPattern(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "AttackPattern",
                "name": "Evil Pattern",
                "x_mitre_id": "T1999",
                "description": "Test Attack Pattern",
            }
        ]

    def ownclass(self):
        return self.api_client.attack_pattern


class TestCourseOfAction(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "CourseOfAction",
                "name": "Evil Pattern",
                "description": "Test Attack Pattern",
            }
        ]

    def ownclass(self):
        return self.api_client.course_of_action


class TestExternalReference(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "ExternalReference",
                "source_name": "veris",
                "description": "Evil veris link",
                "external_id": "001AA7F-C601-424A-B2B8-BE6C9F5164E7",
                "url": "https://github.com/vz-risk/VCDB/blob/125307638178efddd3ecfe2c267ea434667a4eea/data/json/validated/0001AA7F-C601-424A-B2B8-BE6C9F5164E7.json",
            }
        ]

    def ownclass(self):
        return self.api_client.external_reference

    def baseclass(self):
        return self.api_client.external_reference


class TestCampaign(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "Campagin",
                "name": "Green Group Attacks Against Finance",
                "description": "Campaign by Green Group against a series of targets in the financial services sector.",
                "aliases": ["GREENEVIL", "GREVIL"],
                "confidence": 60,
                "first_seen": get_incident_start_date(),
                "last_seen": get_incident_end_date(),
                "objective": "World dominance",
            }
        ]

    def ownclass(self):
        return self.api_client.campaign


class TestIncident(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "Incident",
                "name": "Green Group Attacks Against Finance",
                "description": "Incident by Green Group against a targets in the financial services sector.",
                "aliases": ["GREENEVIL", "GREVIL"],
                "confidence": 60,
                "first_seen": get_incident_start_date(),
                "last_seen": get_incident_end_date(),
                "objective": "World dominance",
            }
        ]

    def ownclass(self):
        return self.api_client.incident


class TestInfrastructure(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "Infrastructure",
                "name": "Poison Ivy C2",
                "description": "Poison Ivy C2 turning into C3",
                "first_seen": get_incident_start_date(),
                "last_seen": get_incident_end_date(),
                "infrastructure_types": ["command-and-control"],
            }
        ]

    def ownclass(self):
        return self.api_client.infrastructure


class TestIntrusionSet(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "IntrusionSet",
                "name": "Bobcat Breakin",
                "description": "Incidents usually feature a shared TTP of a bobcat being released within the building containing network access, scaring users to leave their computers without locking them first. Still determining where the threat actors are getting the bobcats.",
                "aliases": ["Zookeeper"],
                "goals": ["acquisition-theft", "harassment", "damage"],
            }
        ]

    def ownclass(self):
        return self.api_client.intrusion_set


class TestKillChainPhase(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "KillChainPhase",
                "kill_chain_name": "foo",
                "phase_name": "pre-attack",
            }
        ]

    def ownclass(self):
        return self.api_client.kill_chain_phase

    def baseclass(self):
        return self.api_client.kill_chain_phase


class TestLabel(TestEntity):
    def data(self) -> List[Dict]:
        return [{"type": "Label", "value": "foo", "color": "#c3ff1a"}]

    def ownclass(self):
        return self.api_client.label

    def baseclass(self):
        return self.api_client.label


class TestLocation(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": LocationTypes.CITY.value,
                "name": "Mars",
                "description": "A city ",
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
            {
                "type": LocationTypes.COUNTRY.value,
                "name": "Mars",
                "description": "A city ",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "region": "northern-america",
                "country": "th",
                "administrative_area": "Tak",
                "postal_code": "63170",
            },
            {
                "type": LocationTypes.REGION.value,
                "name": "Mars",
                "description": "A city ",
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
            {
                "type": LocationTypes.POSITION.value,
                "name": "CEO",
                "description": "The janitor of everything",
            },
        ]

    def ownclass(self):
        return self.api_client.location


class TestMalware(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "Malware",
                "name": "Cryptolocker",
                "description": "A variant of the cryptolocker family",
                "malware_types": ["ransomware"],
                "is_family": False,
            }
        ]

    def ownclass(self):
        return self.api_client.malware


class TestMarkingDefinition(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "MarkingDefinition",
                "definition_type": "statement",
                # TODO definition should be an array
                "definition": "Copyright 2019, Example Corp",
            }
        ]

    def ownclass(self):
        return self.api_client.marking_definition


class TestObservedData(TestEntity):
    def setup(self):
        self.ipv4 = self.api_client.stix_cyber_observable.create(
            simple_observable_id=OpenCTIStix2Utils.generate_random_stix_id(
                "x-opencti-simple-observable"
            ),
            simple_observable_key="IPv4-Addr.value",
            simple_observable_value="198.51.100.3",
        )
        self.domain = self.api_client.stix_cyber_observable.create(
            simple_observable_id=OpenCTIStix2Utils.generate_random_stix_id(
                "x-opencti-simple-observable"
            ),
            simple_observable_key="Domain-Name.value",
            simple_observable_value="example.com",
        )

    def data(self) -> List[Dict]:
        return [
            {
                "type": "ObservedData",
                "first_observed": "2015-12-21T19:00:00Z",
                "last_observed": "2015-12-21T19:00:00Z",
                "number_observed": 50,
                "object_refs": [self.ipv4["id"], self.domain["id"]],
            }
        ]

    def teardown(self):
        self.api_client.stix_cyber_observable.delete(id=self.ipv4["id"])
        self.api_client.stix_cyber_observable.delete(id=self.domain["id"])

    def ownclass(self):
        return self.api_client.observed_data


class TestNote(TestEntity):
    def data(self) -> List[Dict]:
        return [
            {
                "type": "Note",
                # TODO bug? abstract is key attribute_abstract
                "abstract": "A very short note",
                "content": "You would like to know that",
                "confidence": 50,
                "authors": ["you"],
                # TODO lang is never present!
                "lang": "en",
            }
        ]

    def ownclass(self):
        return self.api_client.note
