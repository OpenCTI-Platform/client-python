# coding: utf-8

import time
import os
import json
import uuid
import base64
import datetime
from typing import List

import datefinder
import dateutil.parser
import pytz

from pycti.utils.constants import (
    IdentityTypes,
    LocationTypes,
    ContainerTypes,
    StixCyberObservableTypes,
)

datefinder.ValueError = ValueError, OverflowError
utc = pytz.UTC

# ObservableRelations
OBSERVABLE_RELATIONS = ["corresponds", "belongs"]

# Spec version
SPEC_VERSION = "2.1"


class OpenCTIStix2:
    """Python API for Stix2 in OpenCTI

    :param opencti: OpenCTI instance
    """

    def __init__(self, opencti):
        self.opencti = opencti
        self.mapping_cache = {}

    ######### UTILS
    # region utils
    def unknown_type(self, stix_object):
        self.opencti.log(
            "error",
            'Unknown object type "' + stix_object["type"] + '", doing nothing...',
        )

    def convert_markdown(self, text) -> str:
        """converts input text to markdown style code annotation

        :param text: input text
        :type text: str
        :return: sanitized text with markdown style code annotation
        :rtype: str
        """

        return text.replace("<code>", "`").replace("</code>", "`")

    def format_date(self, date):
        """converts multiple input date formats to OpenCTI style dates

        :param date: input date
        :type date:
        :return: OpenCTI style date
        :rtype: datetime
        """

        if isinstance(date, datetime.date):
            return date.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        if date is not None:
            return (
                dateutil.parser.parse(date)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )
        else:
            return (
                datetime.datetime.utcnow()
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )

    def filter_objects(self, uuids: list, objects: list) -> list:
        """filters objects based on UUIDs

        :param uuids: list of UUIDs
        :type uuids: list
        :param objects: list of objects to filter
        :type objects: list
        :return: list of filtered objects
        :rtype: list
        """

        result = []
        if objects is not None:
            for item in objects:
                if "id" in item and item["id"] not in uuids:
                    result.append(item)
        return result

    def pick_aliases(self, stix_object) -> list:
        """check stix2 object for multiple aliases and return a list

        :param stix_object: valid stix2 object
        :type stix_object:
        :return: list of aliases
        :rtype: list
        """

        # Add aliases
        if "x_opencti_aliases" in stix_object:
            return stix_object["x_opencti_aliases"]
        elif "x_mitre_aliases" in stix_object:
            return stix_object["x_mitre_aliases"]
        elif "x_amitt_aliases" in stix_object:
            return stix_object["x_amitt_aliases"]
        elif "aliases" in stix_object:
            return stix_object["aliases"]
        return None

    def check_max_marking_definition(
        self, max_marking_definition_entity: str, entity_marking_definitions: list
    ) -> bool:
        """checks if a list of marking definitions conforms with a given max level

        :param max_marking_definition_entity: the maximum allowed marking definition level
        :type max_marking_definition_entity: str, optional
        :param entity_marking_definitions: list of entities to check
        :type entity_marking_definitions: list
        :return: `True` if the list conforms with max marking definition
        :rtype: bool
        """

        # Max is not set, return True
        if max_marking_definition_entity is None:
            return True
        # Filter entity markings definition to the max_marking_definition type
        typed_entity_marking_definitions = []
        for entity_marking_definition in entity_marking_definitions:
            if (
                entity_marking_definition["definition_type"]
                == max_marking_definition_entity["definition_type"]
            ):
                typed_entity_marking_definitions.append(entity_marking_definition)
        # No entity marking defintions of the max_marking_definition type
        if len(typed_entity_marking_definitions) == 0:
            return True

        # Check if level is less or equal to max
        for typed_entity_marking_definition in typed_entity_marking_definitions:
            if (
                typed_entity_marking_definition["x_opencti_order"]
                <= max_marking_definition_entity["x_opencti_order"]
            ):
                return True
        return False

    def import_bundle_from_file(self, file_path: str, update=False, types=None) -> List:
        """import a stix2 bundle from a file

        :param file_path: valid path to the file
        :type file_path: str
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :param types: list of stix2 types, defaults to None
        :type types: list, optional
        :return: list of imported stix2 objects
        :rtype: List
        """
        if not os.path.isfile(file_path):
            self.opencti.log("error", "The bundle file does not exists")
            return None
        with open(os.path.join(file_path)) as file:
            data = json.load(file)
        return self.import_bundle(data, update, types)

    def import_bundle_from_json(self, json_data, update=False, types=None) -> List:
        """import a stix2 bundle from JSON data

        :param json_data: JSON data
        :type json_data:
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :param types: list of stix2 types, defaults to None
        :type types: list, optional
        :return: list of imported stix2 objects
        :rtype: List
        """
        data = json.loads(json_data)
        return self.import_bundle(data, update, types)

    def resolve_author(self, title):
        if "fireeye" in title.lower() or "mandiant" in title.lower():
            return self.get_author("FireEye")
        if "eset" in title.lower():
            return self.get_author("ESET")
        if "dragos" in title.lower():
            return self.get_author("Dragos")
        if "us-cert" in title.lower():
            return self.get_author("US-CERT")
        if (
            "unit 42" in title.lower()
            or "unit42" in title.lower()
            or "palo alto" in title.lower()
        ):
            return self.get_author("Palo Alto Networks")
        if "accenture" in title.lower():
            return self.get_author("Accenture")
        if "symantec" in title.lower():
            return self.get_author("Symantec")
        if "trendmicro" in title.lower() or "trend micro" in title.lower():
            return self.get_author("Trend Micro")
        if "mcafee" in title.lower():
            return self.get_author("McAfee")
        if "crowdstrike" in title.lower():
            return self.get_author("CrowdStrike")
        if "securelist" in title.lower() or "kaspersky" in title.lower():
            return self.get_author("Kaspersky")
        if "f-secure" in title.lower():
            return self.get_author("F-Secure")
        if "checkpoint" in title.lower():
            return self.get_author("CheckPoint")
        if "talos" in title.lower():
            return self.get_author("Cisco Talos")
        if "secureworks" in title.lower():
            return self.get_author("Dell SecureWorks")
        if "microsoft" in title.lower():
            return self.get_author("Microsoft")
        if "mitre att&ck" in title.lower():
            return self.get_author("The MITRE Corporation")
        return None

    def get_author(self, name):
        if name in self.mapping_cache:
            return self.mapping_cache[name]
        else:
            author = self.opencti.identity.create(
                type="Organization", name=name, description="",
            )
            self.mapping_cache[name] = author
            return author

    def extract_embedded_relationships(self, stix_object, types=None) -> dict:
        """extracts embedded relationship objects from a stix2 entity

        :param stix_object: valid stix2 object
        :type stix_object:
        :param types: list of stix2 types, defaults to None
        :type types: list, optional
        :return: embedded relationships as dict
        :rtype: dict
        """

        # Created By Ref
        created_by_id = None
        if "created_by_ref" in stix_object:
            created_by_ref = stix_object["created_by_ref"]
            if created_by_ref in self.mapping_cache:
                created_by_result = self.mapping_cache[created_by_ref]
            else:
                custom_attributes = """
                    id
                    entity_type
                """
                created_by_result = self.opencti.stix_domain_object.read(
                    id=created_by_ref, customAttributes=custom_attributes
                )
                if created_by_result is not None:
                    self.mapping_cache[created_by_ref] = {
                        "id": created_by_result["id"],
                        "type": created_by_result["entity_type"],
                    }
            if created_by_result is not None:
                created_by_id = created_by_result["id"]

        # Object Marking Refs
        object_marking_ids = []
        if "object_marking_refs" in stix_object:
            for object_marking_ref in stix_object["object_marking_refs"]:
                if object_marking_ref in self.mapping_cache:
                    object_marking_ref_result = self.mapping_cache[object_marking_ref]
                else:
                    object_marking_ref_result = self.opencti.marking_definition.read(
                        id=object_marking_ref
                    )
                    if object_marking_ref_result is not None:
                        self.mapping_cache[object_marking_ref] = {
                            "id": object_marking_ref_result["id"],
                            "type": object_marking_ref_result["entity_type"],
                        }
                if object_marking_ref_result is not None:
                    object_marking_ids.append(object_marking_ref_result["id"])

        # Object Tags
        object_label_ids = []
        if "labels" in stix_object:
            for label in stix_object["labels"]:
                if "label_" + label in self.mapping_cache:
                    label_id = self.mapping_cache["label_" + label]
                else:
                    label_id = self.opencti.label.create(value=label)["id"]
                if label_id is not None:
                    object_label_ids.append(label_id)

        # Kill Chain Phases
        kill_chain_phases_ids = []
        if "kill_chain_phases" in stix_object:
            for kill_chain_phase in stix_object["kill_chain_phases"]:
                if (
                    kill_chain_phase["kill_chain_name"] + kill_chain_phase["phase_name"]
                    in self.mapping_cache
                ):
                    kill_chain_phase = self.mapping_cache[
                        kill_chain_phase["kill_chain_name"]
                        + kill_chain_phase["phase_name"]
                    ]
                else:
                    kill_chain_phase = self.opencti.kill_chain_phase.create(
                        kill_chain_name=kill_chain_phase["kill_chain_name"],
                        phase_name=kill_chain_phase["phase_name"],
                        phase_order=kill_chain_phase["x_opencti_order"]
                        if "x_opencti_order" in kill_chain_phase
                        else 0,
                    )
                    self.mapping_cache[
                        kill_chain_phase["kill_chain_name"]
                        + kill_chain_phase["phase_name"]
                    ] = {
                        "id": kill_chain_phase["id"],
                        "type": kill_chain_phase["entity_type"],
                    }
                kill_chain_phases_ids.append(kill_chain_phase["id"])

        # Object refs
        object_refs_ids = []
        if "object_refs" in stix_object:
            for object_ref in stix_object["object_refs"]:
                object_ref_result = None
                if object_ref in self.mapping_cache:
                    object_ref_result = self.mapping_cache[object_ref]
                elif "relationship" in object_ref:
                    object_ref_result = self.opencti.stix_relation.read(id=object_ref)
                    if object_ref_result is not None:
                        self.mapping_cache[object_ref] = {
                            "id": object_ref_result["id"],
                            "type": object_ref_result["entity_type"],
                        }
                elif "observed-data" not in object_ref:
                    object_ref_result = self.opencti.opencti_stix_object_or_stix_relationship.read(
                        id=object_ref
                    )
                    if object_ref_result is not None:
                        self.mapping_cache[object_ref] = {
                            "id": object_ref_result["id"],
                            "type": object_ref_result["entity_type"],
                        }
                if "observed-data" not in object_ref:
                    if object_ref_result is not None:
                        object_refs_ids.append(object_ref_result["id"])
                else:
                    object_refs_ids.append(object_ref)

        # External References
        reports = {}
        external_references_ids = []
        if "external_references" in stix_object:
            for external_reference in stix_object["external_references"]:
                if "url" in external_reference and "source_name" in external_reference:
                    url = external_reference["url"]
                    source_name = external_reference["source_name"]
                else:
                    continue
                if url in self.mapping_cache:
                    external_reference_id = self.mapping_cache[url]["id"]
                else:
                    external_reference_id = self.opencti.external_reference.create(
                        source_name=source_name,
                        url=url,
                        external_id=external_reference["external_id"]
                        if "external_id" in external_reference
                        else None,
                        description=external_reference["description"]
                        if "description" in external_reference
                        else None,
                    )["id"]
                self.mapping_cache[url] = {"id": external_reference_id}
                external_references_ids.append(external_reference_id)

                if stix_object["type"] in [
                    "threat-actor",
                    "intrusion-set",
                    "campaign",
                    "x-opencti-incident",
                    "malware",
                    "relationship",
                ] and (types is None or "report" in types):
                    # Add a corresponding report
                    # Extract date
                    try:
                        if "description" in external_reference:
                            matches = datefinder.find_dates(
                                external_reference["description"]
                            )
                        else:
                            matches = datefinder.find_dates(source_name)
                    except:
                        matches = None
                    published = None
                    today = datetime.datetime.today()
                    if matches is not None:
                        try:
                            for match in matches:
                                if match < today:
                                    published = match.strftime("%Y-%m-%dT%H:%M:%SZ")
                                    break
                        except:
                            published = None
                    if published is None:
                        published = today.strftime("%Y-%m-%dT%H:%M:%SZ")

                    if "mitre" in source_name and "name" in stix_object:
                        title = "[MITRE ATT&CK] " + stix_object["name"]
                        if "modified" in stix_object:
                            published = stix_object["modified"]
                    elif "amitt" in source_name and "name" in stix_object:
                        title = "[AM!TT] " + stix_object["name"]
                        if "modified" in stix_object:
                            published = stix_object["modified"]
                    else:
                        title = source_name

                    if "external_id" in external_reference:
                        title = (
                            title + " (" + str(external_reference["external_id"]) + ")"
                        )

                    if "marking_tlpwhite" in self.mapping_cache:
                        object_marking_ref_result = self.mapping_cache[
                            "marking_tlpwhite"
                        ]
                    else:
                        object_marking_ref_result = self.opencti.marking_definition.read(
                            filters=[
                                {"key": "definition_type", "values": ["TLP"]},
                                {"key": "definition", "values": ["TLP:WHITE"]},
                            ]
                        )
                        self.mapping_cache["marking_tlpwhite"] = {
                            "id": object_marking_ref_result["id"]
                        }

                    author = self.resolve_author(title)
                    report = self.opencti.report.create(
                        name=title,
                        external_reference_id=external_reference_id,
                        createdBy=author["id"] if author is not None else None,
                        objectMarking=[object_marking_ref_result["id"]],
                        description=external_reference["description"]
                        if "description" in external_reference
                        else "",
                        report_types="threat-report",
                        published=published,
                        x_opencti_report_status=2,
                        update=True,
                    )
                    reports[external_reference_id] = report

        return {
            "created_by": created_by_id,
            "object_marking": object_marking_ids,
            "object_label": object_label_ids,
            "kill_chain_phases": kill_chain_phases_ids,
            "object_refs": object_refs_ids,
            "external_references": external_references_ids,
            "reports": reports,
        }

    # endregion

    # region import
    def import_object(self, stix_object, update=False, types=None) -> list:
        """import a stix2 object

        :param stix_object: valid stix2 object
        :type stix_object:
        :param update: whether to updated data in the database, defaults to False
        :type update: bool, optional
        :param types: list of stix2 types, defaults to None
        :type types: list, optional
        :return: list of imported stix2 objects
        :rtype: list
        """

        self.opencti.log(
            "info",
            "Importing a " + stix_object["type"] + " (id: " + stix_object["id"] + ")",
        )

        # Extract
        embedded_relationships = self.extract_embedded_relationships(stix_object, types)
        created_by_id = embedded_relationships["created_by"]
        object_marking_ids = embedded_relationships["object_marking"]
        object_label_ids = embedded_relationships["object_label"]
        kill_chain_phases_ids = embedded_relationships["kill_chain_phases"]
        object_refs_ids = embedded_relationships["object_refs"]
        external_references_ids = embedded_relationships["external_references"]
        reports = embedded_relationships["reports"]

        # Extra
        extras = {
            "created_by_id": created_by_id,
            "object_marking_ids": object_marking_ids,
            "object_label_ids": object_label_ids,
            "kill_chain_phases_ids": kill_chain_phases_ids,
            "object_ids": object_refs_ids,
            "external_references_ids": external_references_ids,
            "reports": reports,
        }

        # Import
        importer = {
            "marking-definition": self.opencti.marking_definition.import_from_stix2,
            "attack-pattern": self.opencti.attack_pattern.import_from_stix2,
            "campaign": self.opencti.campaign.import_from_stix2,
            "note": self.opencti.note.import_from_stix2,
            "observed-data": self.opencti.observed_data.import_from_stix2,
            "opinion": self.opencti.opinion.import_from_stix2,
            "report": self.opencti.report.import_from_stix2,
            "course-of-action": self.opencti.course_of_action.import_from_stix2,
            "identity": self.opencti.identity.import_from_stix2,
            "indicator": self.opencti.indicator.import_from_stix2,
            "infrastructure": self.opencti.infrastructure.import_from_stix2,
            "intrusion-set": self.opencti.intrusion_set.import_from_stix2,
            "location": self.opencti.location.import_from_stix2,
            "malware": self.opencti.malware.import_from_stix2,
            "threat-actor": self.opencti.threat_actor.import_from_stix2,
            "tool": self.opencti.tool.import_from_stix2,
            "vulnerability": self.opencti.vulnerability.import_from_stix2,
            "x-opencti-incident": self.opencti.x_opencti_incident.import_from_stix2,
        }
        do_import = importer.get(
            stix_object["type"], lambda **kwargs: self.unknown_type(stix_object),
        )
        stix_object_results = do_import(
            stixObject=stix_object, extras=extras, update=update
        )

        if stix_object_results is None:
            return stix_object_results

        if not isinstance(stix_object_results, list):
            stix_object_results = [stix_object_results]

        for stix_object_result in stix_object_results:
            self.mapping_cache[stix_object["id"]] = {
                "id": stix_object_result["id"],
                "type": stix_object_result["entity_type"],
            }
            self.mapping_cache[stix_object_result["id"]] = {
                "id": stix_object_result["id"],
                "type": stix_object_result["entity_type"],
            }
            # Add reports from external references
            for external_reference_id in external_references_ids:
                if external_reference_id in reports:
                    self.opencti.report.add_stix_object_or_stix_relationship(
                        id=reports[external_reference_id]["id"],
                        stixObjectOrStixRelationshipId=stix_object_result["id"],
                    )
            # Add object refs
            for object_refs_id in object_refs_ids:
                if stix_object_result["entity_type"] == "report":
                    self.opencti.report.add_stix_object_or_stix_relationship(
                        id=stix_object_result["id"],
                        stixObjectOrStixRelationshipId=object_refs_id,
                    )
                elif stix_object_result["entity_type"] == "observed-data":
                    self.opencti.observed_data.add_stix_object_or_stix_relationship(
                        id=stix_object_result["id"],
                        stixObjectOrStixRelationshipId=object_refs_id,
                    )
                elif stix_object_result["entity_type"] == "note":
                    self.opencti.note.add_stix_object_or_stix_relationship(
                        id=stix_object_result["id"],
                        stixObjectOrStixRelationshipId=object_refs_id,
                    )
                elif stix_object_result["entity_type"] == "opinion":
                    self.opencti.opinion.add_stix_object_or_stix_relationship(
                        id=stix_object_result["id"],
                        stixObjectOrStixRelationshipId=object_refs_id,
                    )
            # Add files
            if "x_opencti_files" in stix_object:
                for file in stix_object["x_opencti_files"]:
                    self.opencti.stix_domain_object.add_file(
                        id=stix_object_result["id"],
                        file_name=file["name"],
                        data=base64.b64decode(file["data"]),
                        mime_type=file["mime_type"],
                    )

        return stix_object_results

    def import_observable(self, stix_object, update=False, types=None):
        # Extract
        embedded_relationships = self.extract_embedded_relationships(stix_object, types)
        created_by_id = embedded_relationships["created_by"]
        object_marking_ids = embedded_relationships["object_marking"]
        object_label_ids = embedded_relationships["object_label"]
        kill_chain_phases_ids = embedded_relationships["kill_chain_phases"]
        object_refs_ids = embedded_relationships["object_refs"]
        external_references_ids = embedded_relationships["external_references"]
        reports = embedded_relationships["reports"]

        # Extra
        extras = {
            "created_by_id": created_by_id,
            "object_marking_ids": object_marking_ids,
            "object_label_ids": object_label_ids,
            "kill_chain_phases_ids": kill_chain_phases_ids,
            "object_ids": object_refs_ids,
            "external_references_ids": external_references_ids,
            "reports": reports,
        }

        stix_observable_result = self.opencti.stix_observable.create(
            observableData=stix_object,
            createdBy=extras["created_by_id"] if "created_by_id" in extras else None,
            objectMarking=extras["object_marking_ids"]
            if "object_marking_ids" in extras
            else [],
            objectLabel=extras["object_label_ids"]
            if "object_label_ids" in extras
            else [],
            externalReferences=extras["external_references_ids"]
            if "external_references_ids" in extras
            else [],
            update=update,
        )
        if stix_observable_result is not None:
            self.mapping_cache[stix_observable_result["id"]] = {
                "id": stix_observable_result["id"],
                "type": stix_observable_result["entity_type"],
            }
        else:
            return None

    def import_relationship(self, stix_relation, update=False, types=None):
        # Extract
        embedded_relationships = self.extract_embedded_relationships(
            stix_relation, types
        )
        created_by_id = embedded_relationships["created_by"]
        object_marking_ids = embedded_relationships["object_marking"]
        object_label_ids = embedded_relationships["object_label"]
        kill_chain_phases_ids = embedded_relationships["kill_chain_phases"]
        object_refs_ids = embedded_relationships["object_refs"]
        external_references_ids = embedded_relationships["external_references"]
        reports = embedded_relationships["reports"]

        # Extra
        extras = {
            "created_by_id": created_by_id,
            "object_marking_ids": object_marking_ids,
            "object_label_ids": object_label_ids,
            "kill_chain_phases_ids": kill_chain_phases_ids,
            "object_ids": object_refs_ids,
            "external_references_ids": external_references_ids,
            "reports": reports,
        }

        # Create the relation

        ## Try to guess start_time / stop_time from external reference
        date = None
        if "external_references" in stix_relation:
            for external_reference in stix_relation["external_references"]:
                try:
                    if "description" in external_reference:
                        matches = datefinder.find_dates(
                            external_reference["description"]
                        )
                    else:
                        matches = datefinder.find_dates(
                            external_reference["source_name"]
                        )
                except:
                    matches = None
                date = None
                today = datetime.datetime.today()
                if matches is not None:
                    try:
                        for match in matches:
                            if match < today:
                                date = match.strftime("%Y-%m-%dT%H:%M:%SZ")
                                break
                    except:
                        date = None

        stix_relation_result = self.opencti.stix_core_relationship.import_from_stix2(
            stixRelation=stix_relation, extras=extras, update=update, defaultDate=date
        )
        if stix_relation_result is not None:
            self.mapping_cache[stix_relation["id"]] = {
                "id": stix_relation_result["id"],
                "type": stix_relation_result["entity_type"],
            }
        else:
            return None

        # Add external references
        for external_reference_id in external_references_ids:
            if external_reference_id in reports:
                self.opencti.report.add_stix_object_or_stix_relationship(
                    id=reports[external_reference_id]["id"],
                    stixObjectOrStixRelationshipId=stix_relation_result["id"],
                )
                self.opencti.report.add_stix_object_or_stix_relationship(
                    id=reports[external_reference_id]["id"],
                    stixObjectOrStixRelationshipId=stix_relation["source_ref"],
                )
                self.opencti.report.add_stix_object_or_stix_relationship(
                    id=reports[external_reference_id]["id"],
                    stixObjectOrStixRelationshipId=stix_relation["target_ref"],
                )

    def import_sighting(self, stix_sighting, from_id, to_id, update=False, types=None):
        # Extract
        embedded_relationships = self.extract_embedded_relationships(
            stix_sighting, types
        )
        created_by_id = embedded_relationships["created_by"]
        object_marking_ids = embedded_relationships["object_marking"]
        object_label_ids = embedded_relationships["object_label"]
        kill_chain_phases_ids = embedded_relationships["kill_chain_phases"]
        object_refs_ids = embedded_relationships["object_refs"]
        external_references_ids = embedded_relationships["external_references"]
        reports = embedded_relationships["reports"]

        # Extra
        extras = {
            "created_by_id": created_by_id,
            "object_marking_ids": object_marking_ids,
            "object_label_ids": object_label_ids,
            "kill_chain_phases_ids": kill_chain_phases_ids,
            "object_ids": object_refs_ids,
            "external_references_ids": external_references_ids,
            "reports": reports,
        }

        # Create the sighting

        ### Get the FROM
        if from_id in self.mapping_cache:
            final_from_id = self.mapping_cache[from_id]["id"]
        else:
            stix_object_result = self.opencti.opencti_stix_object_or_stix_relationship.read(
                id=from_id
            )
            if stix_object_result is not None:
                final_from_id = stix_object_result["id"]
            else:
                self.opencti.log(
                    "error", "From ref of the sithing not found, doing nothing...",
                )
                return None

        ### Get the TO
        final_to_id = None
        if to_id:
            if to_id in self.mapping_cache:
                final_to_id = self.mapping_cache[to_id]["id"]
            else:
                stix_object_result = self.opencti.opencti_stix_object_or_stix_relationship.read(
                    id=to_id
                )
                if stix_object_result is not None:
                    final_to_id = stix_object_result["id"]
                else:
                    self.opencti.log(
                        "error", "To ref of the sithing not found, doing nothing...",
                    )
                    return None
        date = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
        stix_sighting_result = self.opencti.stix_sighting_relationship.create(
            fromId=final_from_id,
            toId=final_to_id,
            stix_id=stix_sighting["id"] if "id" in stix_sighting else None,
            description=self.convert_markdown(stix_sighting["description"])
            if "description" in stix_sighting
            else None,
            first_seen=stix_sighting["first_seen"]
            if "first_seen" in stix_sighting
            else date,
            last_seen=stix_sighting["last_seen"]
            if "last_seen" in stix_sighting
            else date,
            count=stix_sighting["count"] if "count" in stix_sighting else 1,
            x_opencti_negative=stix_sighting["x_opencti_negative"]
            if "x_opencti_negative" in stix_sighting
            else False,
            created=stix_sighting["created"] if "created" in stix_sighting else None,
            modified=stix_sighting["modified"] if "modified" in stix_sighting else None,
            confidence=stix_sighting["confidence"]
            if "confidence" in stix_sighting
            else 15,
            createdBy=extras["created_by_id"] if "created_by_id" in extras else None,
            objectMarking=extras["object_marking_ids"]
            if "object_marking_ids" in extras
            else [],
            objectLabel=extras["object_label_ids"]
            if "object_label_ids" in extras
            else [],
            externalReferences=extras["external_references_ids"]
            if "external_references_ids" in extras
            else [],
            update=update,
            ignore_dates=stix_sighting["x_opencti_ignore_dates"]
            if "x_opencti_ignore_dates" in stix_sighting
            else None,
        )
        if stix_sighting_result is not None:
            self.mapping_cache[stix_sighting["id"]] = {
                "id": stix_sighting_result["id"],
                "type": stix_sighting_result["entity_type"],
            }
        else:
            return None

    # endregion

    # region export
    def prepare_export(
        self, entity, stix_object, mode="simple", max_marking_definition_entity=None
    ):
        if (
            self.check_max_marking_definition(
                max_marking_definition_entity, entity["markingDefinitions"]
            )
            is False
        ):
            self.opencti.log(
                "info",
                "Marking definitions of "
                + stix_object["type"]
                + ' "'
                + stix_object["name"]
                + '" are less than max definition, not exporting.',
            )
            return []
        result = []
        objects_to_get = []
        relations_to_get = []
        if "createdBy" in entity and entity["createdBy"] is not None:
            entity_created_by = entity["createdBy"]
            if entity_created_by["entity_type"] == "user":
                identity_class = "individual"
            elif entity_created_by["entity_type"] == "sector":
                identity_class = "class"
            else:
                identity_class = entity_created_by["entity_type"]

            created_by = dict()
            created_by["id"] = entity_created_by["stix_id"]
            created_by["type"] = "identity"
            created_by["spec_version"] = SPEC_VERSION
            created_by["name"] = entity_created_by["name"]
            created_by["identity_class"] = identity_class
            if self.opencti.not_empty(entity_created_by["stix_label"]):
                created_by["labels"] = entity_created_by["stix_label"]
            else:
                created_by["labels"] = ["identity"]
            created_by["created"] = self.format_date(entity_created_by["created"])
            created_by["modified"] = self.format_date(entity_created_by["modified"])
            if entity_created_by["entity_type"] == "organization":
                if (
                    "x_opencti_organization_type" in entity_created_by
                    and self.opencti.not_empty(
                        entity_created_by["x_opencti_organization_type"]
                    )
                ):
                    created_by[CustomProperties.ORG_CLASS] = entity_created_by[
                        "x_opencti_organization_type"
                    ]
                if (
                    "x_opencti_reliability" in entity_created_by
                    and self.opencti.not_empty(
                        entity_created_by["x_opencti_reliability"]
                    )
                ):
                    created_by[
                        CustomProperties.x_opencti_reliability
                    ] = entity_created_by["x_opencti_reliability"]
            if self.opencti.not_empty(entity_created_by["alias"]):
                created_by[CustomProperties.ALIASES] = entity_created_by["alias"]
            created_by[CustomProperties.IDENTITY_TYPE] = entity_created_by[
                "entity_type"
            ]
            created_by[CustomProperties.ID] = entity_created_by["id"]

            stix_object["created_by"] = created_by["id"]
            result.append(created_by)
        if "markingDefinitions" in entity and len(entity["markingDefinitions"]) > 0:
            marking_definitions = []
            for entity_marking_definition in entity["markingDefinitions"]:
                if entity_marking_definition["definition_type"] == "TLP":
                    created = "2017-01-20T00:00:00.000Z"
                else:
                    created = entity_marking_definition["created"]
                marking_definition = {
                    "type": "marking-definition",
                    "spec_version": SPEC_VERSION,
                    "id": entity_marking_definition["stix_id"],
                    "created": created,
                    "definition_type": entity_marking_definition[
                        "definition_type"
                    ].lower(),
                    "name": entity_marking_definition["definition"],
                    "definition": {
                        entity_marking_definition["definition_type"]
                        .lower(): entity_marking_definition["definition"]
                        .lower()
                        .replace("tlp:", "")
                    },
                }
                marking_definitions.append(marking_definition["id"])
                result.append(marking_definition)
            stix_object["object_marking_refs"] = marking_definitions
        if "tags" in entity and len(entity["tags"]) > 0:
            tags = []
            for entity_tag in entity["tags"]:
                tag = dict()
                tag["id"] = entity_tag["id"]
                tag["tag_type"] = entity_tag["tag_type"]
                tag["value"] = entity_tag["value"]
                tag["color"] = entity_tag["color"]
                tags.append(tag)
            stix_object[CustomProperties.TAG_TYPE] = tags
        if "killChainPhases" in entity and len(entity["killChainPhases"]) > 0:
            kill_chain_phases = []
            for entity_kill_chain_phase in entity["killChainPhases"]:
                kill_chain_phase = {
                    "id": entity_kill_chain_phase["stix_id"],
                    "kill_chain_name": entity_kill_chain_phase["kill_chain_name"],
                    "phase_name": entity_kill_chain_phase["phase_name"],
                    CustomProperties.ID: entity_kill_chain_phase["id"],
                    CustomProperties.PHASE_ORDER: entity_kill_chain_phase[
                        "phase_order"
                    ],
                    CustomProperties.CREATED: entity_kill_chain_phase["created"],
                    CustomProperties.MODIFIED: entity_kill_chain_phase["modified"],
                }
                kill_chain_phases.append(kill_chain_phase)
            stix_object["kill_chain_phases"] = kill_chain_phases
        if "externalReferences" in entity and len(entity["externalReferences"]) > 0:
            external_references = []
            for entity_external_reference in entity["externalReferences"]:
                external_reference = dict()
                external_reference["id"] = entity_external_reference["stix_id"]
                if self.opencti.not_empty(entity_external_reference["source_name"]):
                    external_reference["source_name"] = entity_external_reference[
                        "source_name"
                    ]
                if self.opencti.not_empty(entity_external_reference["description"]):
                    external_reference["description"] = entity_external_reference[
                        "description"
                    ]
                if self.opencti.not_empty(entity_external_reference["url"]):
                    external_reference["url"] = entity_external_reference["url"]
                if self.opencti.not_empty(entity_external_reference["hash"]):
                    external_reference["hash"] = entity_external_reference["hash"]
                if self.opencti.not_empty(entity_external_reference["external_id"]):
                    external_reference["external_id"] = entity_external_reference[
                        "external_id"
                    ]
                external_reference[CustomProperties.ID] = entity_external_reference[
                    "id"
                ]
                external_reference[
                    CustomProperties.CREATED
                ] = entity_external_reference["created"]
                external_reference[
                    CustomProperties.MODIFIED
                ] = entity_external_reference["modified"]
                external_references.append(external_reference)
            stix_object["external_references"] = external_references
        if "objectRefs" in entity and len(entity["objectRefs"]) > 0:
            object_refs = []
            objects_to_get = entity["objectRefs"]
            for entity_object_ref in entity["objectRefs"]:
                object_refs.append(entity_object_ref["stix_id"])
            if "relationRefs" in entity and len(entity["relationRefs"]) > 0:
                relations_to_get = entity["relationRefs"]
                for entity_relation_ref in entity["relationRefs"]:
                    if entity_relation_ref["stix_id"] not in object_refs:
                        object_refs.append(entity_relation_ref["stix_id"])
            stix_object["object_refs"] = object_refs

        uuids = [stix_object["id"]]
        for x in result:
            uuids.append(x["id"])

        observables_stix_ids = []
        observable_object_data = None
        if "observableRefs" in entity and len(entity["observableRefs"]) > 0:
            observable_object_data = self.export_stix_observables(entity)
            if observable_object_data is not None:
                observable_object_bundle = self.filter_objects(
                    uuids, [observable_object_data["observedData"]]
                )
                uuids = uuids + [x["id"] for x in observable_object_bundle]
                result = result + observable_object_bundle
                observables_stix_ids = (
                    observables_stix_ids + observable_object_data["stixIds"]
                )
                if stix_object["type"] == "report":
                    if "object_refs" in stix_object:
                        stix_object["object_refs"].append(
                            observable_object_data["observedData"]["id"]
                        )
                    else:
                        stix_object["object_refs"] = [
                            observable_object_data["observedData"]["id"]
                        ]
        result.append(stix_object)

        if mode == "simple":
            return result
        elif mode == "full":
            # Get extra relations
            stix_relations = self.opencti.stix_relation.list(
                fromId=entity["id"], forceNatural=True
            )
            for stix_relation in stix_relations:
                if self.check_max_marking_definition(
                    max_marking_definition_entity, stix_relation["markingDefinitions"]
                ):
                    if stix_relation["to"]["id"] == entity["id"]:
                        other_side_entity = stix_relation["from"]
                    else:
                        other_side_entity = stix_relation["to"]
                    objects_to_get.append(other_side_entity)
                    if other_side_entity["stix_id"] in observables_stix_ids:
                        other_side_entity["stix_id"] = observable_object_data[
                            "observedData"
                        ]["id"]
                    relation_object_data = self.opencti.stix_relation.to_stix2(
                        entity=stix_relation
                    )
                    relation_object_bundle = self.filter_objects(
                        uuids, relation_object_data
                    )
                    uuids = uuids + [x["id"] for x in relation_object_bundle]
                    result = result + relation_object_bundle
                else:
                    self.opencti.log(
                        "info",
                        "Marking definitions of "
                        + stix_relation["entity_type"]
                        + ' "'
                        + stix_relation["id"]
                        + '" are less than max definition, not exporting the relation AND the target entity.',
                    )
            # Export
            exporter = {
                "identity": self.opencti.identity.to_stix2,
                "threat-actor": self.opencti.threat_actor.to_stix2,
                "intrusion-set": self.opencti.intrusion_set.to_stix2,
                "campaign": self.opencti.campaign.to_stix2,
                "incident": self.opencti.x_opencti_incident.to_stix2,
                "malware": self.opencti.malware.to_stix2,
                "tool": self.opencti.tool.to_stix2,
                "vulnerability": self.opencti.vulnerability.to_stix2,
                "attack-pattern": self.opencti.attack_pattern.to_stix2,
                "course-of-action": self.opencti.course_of_action.to_stix2,
                "report": self.opencti.report.to_stix2,
                "note": self.opencti.note.to_stix2,
                "opinion": self.opencti.opinion.to_stix2,
                "indicator": self.opencti.indicator.to_stix2,
            }

            # Get extra objects
            for entity_object in objects_to_get:
                # Map types
                if IdentityTypes.has_value(entity_object["entity_type"]):
                    entity_object["entity_type"] = "identity"
                do_export = exporter.get(
                    entity_object["entity_type"],
                    lambda **kwargs: self.unknown_type(
                        {"type": entity_object["entity_type"]}
                    ),
                )
                entity_object_data = do_export(id=entity_object["id"])
                # Add to result
                entity_object_bundle = self.filter_objects(uuids, entity_object_data)
                uuids = uuids + [x["id"] for x in entity_object_bundle]
                result = result + entity_object_bundle
            for relation_object in relations_to_get:
                relation_object_data = self.opencti.stix_relation.to_stix2(
                    id=relation_object["id"]
                )
                relation_object_bundle = self.filter_objects(
                    uuids, relation_object_data
                )
                uuids = uuids + [x["id"] for x in relation_object_bundle]
                result = result + relation_object_bundle

            # Get extra reports
            """
            for uuid in uuids:
                if "marking-definition" not in uuid:
                    reports = self.opencti.opencti_stix_object_or_stix_relationship.reports(id=uuid)
                    for report in reports:
                        report_object_data = self.opencti.report.to_stix2(
                            entity=report,
                            mode="simple",
                            max_marking_definition_entity=max_marking_definition_entity,
                        )
                        report_object_bundle = self.filter_objects(
                            uuids, report_object_data
                        )
                        uuids = uuids + [x["id"] for x in report_object_bundle]
                        result = result + report_object_bundle
            """

            # Get notes
            for export_uuid in uuids:
                if "marking-definition" not in export_uuid:
                    notes = self.opencti.opencti_stix_object_or_stix_relationship.notes(
                        id=export_uuid
                    )
                    for note in notes:
                        note_object_data = self.opencti.note.to_stix2(
                            entity=note,
                            mode="simple",
                            max_marking_definition_entity=max_marking_definition_entity,
                        )
                        note_object_bundle = self.filter_objects(
                            uuids, note_object_data
                        )
                        uuids = uuids + [x["id"] for x in note_object_bundle]
                        result = result + note_object_bundle

            # Refilter all the reports object refs
            final_result = []
            for entity in result:
                if entity["type"] == "report" or entity["type"] == "note":
                    if "object_refs" in entity:
                        entity["object_refs"] = [
                            k for k in entity["object_refs"] if k in uuids
                        ]
                    final_result.append(entity)
                else:
                    final_result.append(entity)
            return final_result
        else:
            return []

    def export_entity(
        self, entity_type, entity_id, mode="simple", max_marking_definition=None
    ):
        max_marking_definition_entity = (
            self.opencti.marking_definition.read(id=max_marking_definition)
            if max_marking_definition is not None
            else None
        )
        bundle = {
            "type": "bundle",
            "id": "bundle--" + str(uuid.uuid4()),
            "objects": [],
        }
        # Map types
        if IdentityTypes.has_value(entity_type):
            entity_type = "identity"

        # Export
        exporter = {
            "identity": self.opencti.identity.to_stix2,
            "threat-actor": self.opencti.threat_actor.to_stix2,
            "intrusion-set": self.opencti.intrusion_set.to_stix2,
            "campaign": self.opencti.campaign.to_stix2,
            "incident": self.opencti.x_opencti_incident.to_stix2,
            "malware": self.opencti.malware.to_stix2,
            "tool": self.opencti.tool.to_stix2,
            "vulnerability": self.opencti.vulnerability.to_stix2,
            "attack-pattern": self.opencti.attack_pattern.to_stix2,
            "course-of-action": self.opencti.course_of_action.to_stix2,
            "report": self.opencti.report.to_stix2,
            "note": self.opencti.note.to_stix2,
            "opinion": self.opencti.opinion.to_stix2,
            "indicator": self.opencti.indicator.to_stix2,
        }
        do_export = exporter.get(
            entity_type, lambda **kwargs: self.unknown_type({"type": entity_type})
        )
        objects = do_export(
            id=entity_id,
            mode=mode,
            max_marking_definition_entity=max_marking_definition_entity,
        )
        if objects is not None:
            bundle["objects"].extend(objects)
        return bundle

    def export_list(
        self,
        entity_type,
        search=None,
        filters=None,
        order_by=None,
        order_mode=None,
        max_marking_definition=None,
        types=None,
    ):
        max_marking_definition_entity = (
            self.opencti.marking_definition.read(id=max_marking_definition)
            if max_marking_definition is not None
            else None
        )
        bundle = {
            "type": "bundle",
            "id": "bundle--" + str(uuid.uuid4()),
            "objects": [],
        }

        if IdentityTypes.has_value(entity_type):
            if filters is not None:
                filters.append({"key": "entity_type", "values": [entity_type]})
            else:
                filters = [{"key": "entity_type", "values": [entity_type]}]
            entity_type = "Identity"

        if IdentityTypes.has_value(entity_type):
            if filters is not None:
                filters.append({"key": "entity_type", "values": [entity_type]})
            else:
                filters = [{"key": "entity_type", "values": [entity_type]}]
            entity_type = "Identity"

        # List
        lister = {
            "Attack-Pattern": self.opencti.attack_pattern.list,
            "campaign": self.opencti.campaign.list,
            "note": self.opencti.note.list,
            "observed-data": self.opencti.observed_data.list,
            "identity": self.opencti.identity.list,
            "threat-actor": self.opencti.threat_actor.list,
            "intrusion-set": self.opencti.intrusion_set.list,
            "incident": self.opencti.x_opencti_incident.list,
            "malware": self.opencti.malware.list,
            "tool": self.opencti.tool.list,
            "vulnerability": self.opencti.vulnerability.list,
            "course-of-action": self.opencti.course_of_action.list,
            "report": self.opencti.report.list,
            "opinion": self.opencti.opinion.list,
            "indicator": self.opencti.indicator.list,
            "stix-observable": self.opencti.stix_observable.list,
        }
        do_list = lister.get(
            entity_type, lambda **kwargs: self.unknown_type({"type": entity_type})
        )
        entities_list = do_list(
            search=search,
            filters=filters,
            orderBy=order_by,
            orderMode=order_mode,
            types=types,
            getAll=True,
        )

        if entities_list is not None:
            # Export
            exporter = {
                "identity": self.opencti.identity.to_stix2,
                "threat-actor": self.opencti.threat_actor.to_stix2,
                "intrusion-set": self.opencti.intrusion_set.to_stix2,
                "campaign": self.opencti.campaign.to_stix2,
                "incident": self.opencti.x_opencti_incident.to_stix2,
                "malware": self.opencti.malware.to_stix2,
                "tool": self.opencti.tool.to_stix2,
                "vulnerability": self.opencti.vulnerability.to_stix2,
                "attack-pattern": self.opencti.attack_pattern.to_stix2,
                "course-of-action": self.opencti.course_of_action.to_stix2,
                "report": self.opencti.report.to_stix2,
                "note": self.opencti.note.to_stix2,
                "opinion": self.opencti.opinion.to_stix2,
                "indicator": self.opencti.indicator.to_stix2,
                "stix-observable": self.opencti.stix_observable.to_stix2,
            }
            do_export = exporter.get(
                entity_type, lambda **kwargs: self.unknown_type({"type": entity_type})
            )
            uuids = []
            for entity in entities_list:
                entity_bundle = do_export(
                    entity=entity,
                    max_marking_definition_entity=max_marking_definition_entity,
                )
                if entity_bundle is not None:
                    entity_bundle_filtered = self.filter_objects(uuids, entity_bundle)
                    for x in entity_bundle_filtered:
                        uuids.append(x["id"])
                    bundle["objects"] = bundle["objects"] + entity_bundle_filtered

        return bundle

    def export_stix_observables(self, entity):
        stix_ids = []
        observed_data = dict()
        observed_data["id"] = "observed-data--" + str(uuid.uuid4())
        observed_data["type"] = "observed-data"
        observed_data["number_observed"] = len(entity["observableRefs"])
        observed_data["objects"] = []
        for observable in entity["observableRefs"]:
            stix_observable = dict()
            stix_observable[CustomProperties.OBSERVABLE_TYPE] = observable[
                "entity_type"
            ]
            stix_observable[CustomProperties.OBSERVABLE_VALUE] = observable[
                "observable_value"
            ]
            stix_observable["type"] = observable["entity_type"]
            observed_data["objects"].append(stix_observable)
            stix_ids.append(observable["stix_id"])

        return {"observedData": observed_data, "stixIds": stix_ids}

    def import_bundle(self, stix_bundle, update=False, types=None) -> List:
        # Check if the bundle is correctly formatted
        if "type" not in stix_bundle or stix_bundle["type"] != "bundle":
            raise ValueError("JSON data type is not a STIX2 bundle")
        if "objects" not in stix_bundle or len(stix_bundle["objects"]) == 0:
            raise ValueError("JSON data objects is empty")

        # Import every elements in a specific order
        imported_elements = []

        # Marking definitions
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "marking-definition":
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info",
            "Marking definitions imported in: %ssecs" % round(end_time - start_time),
        )

        # Identities
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "identity" and (types is None or "identity" in types):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Identities imported in: %ssecs" % round(end_time - start_time)
        )

        # StixCyberObservables
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if StixCyberObservableTypes.has_value(item["type"]):
                self.import_observable(item)
        end_time = time.time()
        self.opencti.log(
            "info", "Observables imported in: %ssecs" % round(end_time - start_time)
        )

        # StixDomainObjects except Report/Opinion/Notes
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if (
                not ContainerTypes.has_value(item["type"])
                and item["type"] != "relationship"
                and item["type"] != "sighting"
            ):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Objects imported in: %ssecs" % round(end_time - start_time)
        )

        # StixCyberObservableRelationships
        # TODO

        # StixRelationObjects
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "relationship":
                split_source_ref = item["source_ref"].split("--")
                split_target_ref = item["target_ref"].split("--")
                if (
                    not ContainerTypes.has_value(split_source_ref[0])
                    and split_source_ref[0] != "relationship"
                    and not ContainerTypes.has_value(split_target_ref[0])
                    and split_target_ref[0] != "relationship"
                ):
                    self.import_relationship(item, update, types)
                    imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Relationships imported in: %ssecs" % round(end_time - start_time)
        )

        # StixRelationObjects (with relationships)
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "relationship":
                if item["type"] == "relationship" and (
                    "relationship--" in item["source_ref"]
                    or "relationship--" in item["target_ref"]
                ):
                    self.import_relationship(item, update, types)
                    imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info",
            "Relationships to relationships imported in: %ssecs"
            % round(end_time - start_time),
        )

        # ObservedDatas
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "observed-data" and (
                types is None or "observed-data" in types
            ):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Observed-Datas imported in: %ssecs" % round(end_time - start_time)
        )

        # StixSightingsObjects
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "sighting":
                # Resolve the to
                to_ids = []
                if "where_sighted_refs" in item:
                    for where_sighted_ref in item["where_sighted_refs"]:
                        to_ids.append(where_sighted_ref)

                # Import sighting_of_ref
                from_id = item["sighting_of_ref"]
                if len(to_ids) > 0:
                    for to_id in to_ids:
                        self.import_sighting(item, from_id, to_id, update)

                # Import observed_data_refs
                if "observed_data_refs" in item:
                    for observed_data_ref in item["observed_data_refs"]:
                        if observed_data_ref in self.mapping_cache:
                            for from_element in self.mapping_cache[observed_data_ref]:
                                if len(to_ids) > 0:
                                    for to_id in to_ids:
                                        self.import_sighting(
                                            item, from_element["id"], to_id, update
                                        )
                                else:
                                    self.import_sighting(item, from_id, None, update)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Sightings imported in: %ssecs" % round(end_time - start_time)
        )

        # Notes
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "note" and (types is None or "note" in types):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Notes imported in: %ssecs" % round(end_time - start_time)
        )

        # Opinions
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "opinion" and (types is None or "opinion" in types):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Opinions imported in: %ssecs" % round(end_time - start_time)
        )

        # StixRelationObjects (with containers)
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "relationship":
                split_source_ref = item["source_ref"].split("--")
                split_target_ref = item["target_ref"].split("--")
                if (
                    split_source_ref[0] != "report"
                    and split_target_ref[0] != "report"
                    and (
                        ContainerTypes.has_value(split_source_ref[0])
                        or ContainerTypes.has_value(split_target_ref[0])
                    )
                ):
                    self.import_relationship(item, update, types)
                    imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info",
            "Relationships to containers imported in: %ssecs"
            % round(end_time - start_time),
        )

        # Reports
        start_time = time.time()
        for item in stix_bundle["objects"]:
            if item["type"] == "report" and (types is None or "report" in types):
                self.import_object(item, update, types)
                imported_elements.append({"id": item["id"], "type": item["type"]})
        end_time = time.time()
        self.opencti.log(
            "info", "Reports imported in: %ssecs" % round(end_time - start_time)
        )

        return imported_elements
