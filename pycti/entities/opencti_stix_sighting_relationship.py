"""OpenCTI Sighting operations"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Union

from . import _generate_uuid5

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "StixSightingRelationship",
]

log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]


class StixSightingRelationship:
    """Sighting relationship object"""

    def __init__(self, api: "OpenCTIApiClient"):
        """
        Constructor.

        :param api: OpenCTI API client
        """

        self._api = api
        self._default_attributes = """
            id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            standard_id
            description
            first_seen
            last_seen
            attribute_count
            x_opencti_negative
            created
            modified
            confidence
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    identity_class
                    name
                    description
                    roles
                    contact_information
                    x_opencti_aliases
                    created
                    modified
                    objectLabel {
                        edges {
                            node {
                                id
                                value
                                color
                            }
                        }
                    }
                }
                ... on Organization {
                    x_opencti_organization_type
                    x_opencti_reliability
                }
                ... on Individual {
                    x_opencti_firstname
                    x_opencti_lastname
                }
            }
            objectMarking {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        definition_type
                        definition
                        created
                        modified
                        x_opencti_order
                        x_opencti_color
                    }
                }
            }
            objectLabel {
                edges {
                    node {
                        id
                        value
                        color
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                }
            }
            from {
                ... on BasicObject {
                    id
                    entity_type
                    parent_types
                }
                ... on BasicRelationship {
                    id
                    entity_type
                    parent_types
                }
                ... on StixObject {
                    standard_id
                    spec_version
                    created_at
                    updated_at
                }
                ... on AttackPattern {
                    name
                }
                ... on Campaign {
                    name
                }
                ... on CourseOfAction {
                    name
                }
                ... on Individual {
                    name
                }
                ... on Organization {
                    name
                }
                ... on Sector {
                    name
                }
                 ... on System {
                    name
                }
                ... on Indicator {
                    name
                }
                ... on Infrastructure {
                    name
                }
                ... on IntrusionSet {
                    name
                }
                ... on Position {
                    name
                }
                ... on City {
                    name
                }
                ... on Country {
                    name
                }
                ... on Region {
                    name
                }
                ... on Malware {
                    name
                }
                ... on ThreatActor {
                    name
                }
                ... on Tool {
                    name
                }
                ... on Vulnerability {
                    name
                }
                ... on Incident {
                    name
                }
                ... on StixCyberObservable {
                    observable_value
                }
                ... on StixCoreRelationship {
                    standard_id
                    spec_version
                    created_at
                    updated_at
                }
            }
            to {
                ... on BasicObject {
                    id
                    entity_type
                    parent_types
                }
                ... on BasicRelationship {
                    id
                    entity_type
                    parent_types
                }
                ... on StixObject {
                    standard_id
                    spec_version
                    created_at
                    updated_at
                }
                ... on AttackPattern {
                    name
                }
                ... on Campaign {
                    name
                }
                ... on CourseOfAction {
                    name
                }
                ... on Individual {
                    name
                }
                ... on Organization {
                    name
                }
                ... on Sector {
                    name
                }
                ... on System {
                    name
                }
                ... on Indicator {
                    name
                }
                ... on Infrastructure {
                    name
                }
                ... on IntrusionSet {
                    name
                }
                ... on Position {
                    name
                }
                ... on City {
                    name
                }
                ... on Country {
                    name
                }
                ... on Region {
                    name
                }
                ... on Malware {
                    name
                }
                ... on ThreatActor {
                    name
                }
                ... on Tool {
                    name
                }
                ... on Vulnerability {
                    name
                }
                ... on Incident {
                    name
                }
                ... on StixCyberObservable {
                    observable_value
                }
                ... on StixCoreRelationship {
                    standard_id
                    spec_version
                    created_at
                    updated_at
                }
            }
        """

    @staticmethod
    def generate_id(
        source_ref: str,
        target_ref: str,
        first_seen: Union[str, datetime] = None,
        last_seen: Union[str, datetime] = None,
    ):
        """
        Generate a STIX compliant UUID5.

        :param source_ref: Relationship source
        :param target_ref: Relationship target
        :param first_seen: When the sighting was first seen
        :param last_seen: When the sighting was last seen
        :return: A Stix compliant UUID5
        """

        if isinstance(first_seen, datetime):
            first_seen = first_seen.isoformat()
        if isinstance(last_seen, datetime):
            last_seen = last_seen.isoformat()

        data = {
            "source_ref": source_ref,
            "target_ref": target_ref,
        }

        if first_seen is not None and last_seen is not None:
            data["first_seen"] = first_seen
            data["last_seen"] = last_seen

        return _generate_uuid5("sighting", data)

    """
        List stix_sightings objects

        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param firstSeenStart: the first_seen date start filter
        :param firstSeenStop: the first_seen date stop filter
        :param lastSeenStart: the last_seen date start filter
        :param lastSeenStop: the last_seen date stop filter
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of stix_sighting objects
    """

    def list(self, **kwargs):
        element_id = kwargs.get("elementId", None)
        from_id = kwargs.get("fromId", None)
        from_types = kwargs.get("fromTypes", None)
        to_id = kwargs.get("toId", None)
        to_types = kwargs.get("toTypes", None)
        first_seen_start = kwargs.get("firstSeenStart", None)
        first_seen_stop = kwargs.get("firstSeenStop", None)
        last_seen_start = kwargs.get("lastSeenStart", None)
        last_seen_stop = kwargs.get("lastSeenStop", None)
        filters = kwargs.get("filters", [])
        first = kwargs.get("first", 100)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 100

        self._api.log(
            "info",
            "Listing stix_sighting with {type: stix_sighting, from_id: "
            + str(from_id)
            + ", to_id: "
            + str(to_id)
            + "}",
        )
        query = (
            """
                                            query StixSightingRelationships($elementId: String, $fromId: String, $fromTypes: [String], $toId: String, $toTypes: [String], $firstSeenStart: DateTime, $firstSeenStop: DateTime, $lastSeenStart: DateTime, $lastSeenStop: DateTime, $filters: [StixSightingRelationshipsFiltering], $first: Int, $after: ID, $orderBy: StixSightingRelationshipsOrdering, $orderMode: OrderingMode) {
                                                stixSightingRelationships(elementId: $elementId, fromId: $fromId, fromTypes: $fromTypes, toId: $toId, toTypes: $toTypes, firstSeenStart: $firstSeenStart, firstSeenStop: $firstSeenStop, lastSeenStart: $lastSeenStart, lastSeenStop: $lastSeenStop, filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                                                    edges {
                                                        node {
                                                            """
            + (
                custom_attributes
                if custom_attributes is not None
                else self._default_attributes
            )
            + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
         """
        )
        result = self._api.query(
            query,
            {
                "elementId": element_id,
                "fromId": from_id,
                "fromTypes": from_types,
                "toId": to_id,
                "toTypes": to_types,
                "firstSeenStart": first_seen_start,
                "firstSeenStop": first_seen_stop,
                "lastSeenStart": last_seen_start,
                "lastSeenStop": last_seen_stop,
                "filters": filters,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        if get_all:
            final_data = []
            data = self._api.process_multiple(
                result["data"]["stixSightingRelationships"]
            )
            final_data = final_data + data
            while result["data"]["stixSightingRelationships"]["pageInfo"][
                "hasNextPage"
            ]:
                after = result["data"]["stixSightingRelationships"]["pageInfo"][
                    "endCursor"
                ]
                self._api.log(
                    "info", "Listing StixSightingRelationships after " + after
                )
                result = self._api.query(
                    query,
                    {
                        "elementId": element_id,
                        "fromId": from_id,
                        "fromTypes": from_types,
                        "toId": to_id,
                        "toTypes": to_types,
                        "firstSeenStart": first_seen_start,
                        "firstSeenStop": first_seen_stop,
                        "lastSeenStart": last_seen_start,
                        "lastSeenStop": last_seen_stop,
                        "filters": filters,
                        "first": first,
                        "after": after,
                        "orderBy": order_by,
                        "orderMode": order_mode,
                    },
                )
                data = self._api.process_multiple(
                    result["data"]["stixSightingRelationships"]
                )
                final_data = final_data + data
            return final_data
        else:
            return self._api.process_multiple(
                result["data"]["stixSightingRelationships"], with_pagination
            )

    """
        Read a stix_sighting object

        :param id: the id of the stix_sighting
        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param firstSeenStart: the first_seen date start filter
        :param firstSeenStop: the first_seen date stop filter
        :param lastSeenStart: the last_seen date start filter
        :param lastSeenStop: the last_seen date stop filter
        :return stix_sighting object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        element_id = kwargs.get("elementId", None)
        from_id = kwargs.get("fromId", None)
        to_id = kwargs.get("toId", None)
        first_seen_start = kwargs.get("firstSeenStart", None)
        first_seen_stop = kwargs.get("firstSeenStop", None)
        last_seen_start = kwargs.get("lastSeenStart", None)
        last_seen_stop = kwargs.get("lastSeenStop", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading stix_sighting {" + id + "}.")
            query = (
                """
                                                query StixSightingRelationship($id: String!) {
                                                    stixSightingRelationship(id: $id) {
                                                        """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self._default_attributes
                )
                + """
                    }
                }
             """
            )
            result = self._api.query(query, {"id": id})
            return self._api.process_multiple_fields(
                result["data"]["stixSightingRelationship"]
            )
        elif from_id is not None and to_id is not None:
            result = self.list(
                elementId=element_id,
                fromId=from_id,
                toId=to_id,
                firstSeenStart=first_seen_start,
                firstSeenStop=first_seen_stop,
                lastSeenStart=last_seen_start,
                lastSeenStop=last_seen_stop,
            )
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log("error", "Missing parameters: id or from_id and to_id")
            return None

    """
        Create a stix_sighting object

        :param name: the name of the Attack Pattern
        :return stix_sighting object
    """

    def create(self, **kwargs):
        from_id = kwargs.get("fromId", None)
        to_id = kwargs.get("toId", None)
        stix_id = kwargs.get("stix_id", None)
        description = kwargs.get("description", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        count = kwargs.get("count", None)
        x_opencti_negative = kwargs.get("x_opencti_negative", False)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        confidence = kwargs.get("confidence", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        self._api.log(
            "info",
            "Creating stix_sighting {" + from_id + ", " + str(to_id) + "}.",
        )
        query = """
                mutation StixSightingRelationshipAdd($input: StixSightingRelationshipAddInput!) {
                    stixSightingRelationshipAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                    }
                }
            """
        result = self._api.query(
            query,
            {
                "input": {
                    "fromId": from_id,
                    "toId": to_id,
                    "stix_id": stix_id,
                    "description": description,
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                    "attribute_count": count,
                    "x_opencti_negative": x_opencti_negative,
                    "created": created,
                    "modified": modified,
                    "confidence": confidence,
                    "createdBy": created_by,
                    "objectMarking": object_marking,
                    "objectLabel": object_label,
                    "externalReferences": external_references,
                    "x_opencti_stix_ids": x_opencti_stix_ids,
                    "update": update,
                }
            },
        )
        return self._api.process_multiple_fields(
            result["data"]["stixSightingRelationshipAdd"]
        )

    """
        Update a stix_sighting object field

        :param id: the stix_sighting id
        :param input: the input of the field
        :return The updated stix_sighting object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        if id is not None and input is not None:
            self._api.log("info", "Updating stix_sighting {" + id + "}")
            query = """
                    mutation StixSightingRelationshipEdit($id: ID!, $input: [EditInput]!) {
                        stixSightingRelationshipEdit(id: $id) {
                            fieldPatch(input: $input) {
                                id
                            }
                        }
                    }
                """
            result = self._api.query(
                query,
                {
                    "id": id,
                    "input": input,
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["stixSightingRelationshipEdit"]["fieldPatch"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_stix_sighting] Missing parameters: id and key and value",
            )
            return None

    """
        Add a Marking-Definition object to stix_sighting_relationship object (object_marking_refs)

        :param id: the id of the stix_sighting_relationship
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_marking_definition(self, **kwargs):
        id = kwargs.get("id", None)
        marking_definition_id = kwargs.get("marking_definition_id", None)
        if id is not None and marking_definition_id is not None:
            custom_attributes = """
                id
                objectMarking {
                    edges {
                        node {
                            id
                            standard_id
                            entity_type
                            definition_type
                            definition
                            x_opencti_order
                            x_opencti_color
                            created
                            modified
                        }
                    }
                }
            """
            stix_core_relationship = self.read(
                id=id, customAttributes=custom_attributes
            )
            if stix_core_relationship is None:
                self._api.log(
                    "error", "Cannot add Marking-Definition, entity not found"
                )
                return False
            if marking_definition_id in stix_core_relationship["objectMarkingIds"]:
                return True
            else:
                self._api.log(
                    "info",
                    "Adding Marking-Definition {"
                    + marking_definition_id
                    + "} to stix_sighting_relationship {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixSightingRelationshipEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                       stixSightingRelationshipEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self._api.query(
                    query,
                    {
                        "id": id,
                        "input": {
                            "toId": marking_definition_id,
                            "relationship_type": "object-marking",
                        },
                    },
                )
                return True
        else:
            self._api.log("error", "Missing parameters: id and marking_definition_id")
            return False

    """
        Remove a Marking-Definition object to stix_sighting_relationship

        :param id: the id of the stix_sighting_relationship
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def remove_marking_definition(self, **kwargs):
        id = kwargs.get("id", None)
        marking_definition_id = kwargs.get("marking_definition_id", None)
        if id is not None and marking_definition_id is not None:
            self._api.log(
                "info",
                "Removing Marking-Definition {"
                + marking_definition_id
                + "} from stix_sighting_relationship {"
                + id
                + "}",
            )
            query = """
               mutation StixSightingRelationshipEdit($id: ID!, $toId: String!, $relationship_type: String!) {
                   stixSightingRelationshipEdit(id: $id) {
                        relationDelete(toId: $toId, relationship_type: $relationship_type) {
                            id
                        }
                   }
               }
            """
            self._api.query(
                query,
                {
                    "id": id,
                    "toId": marking_definition_id,
                    "relationship_type": "object-marking",
                },
            )
            return True
        else:
            self._api.log("error", "Missing parameters: id and label_id")
            return False

    """
        Update the Identity author of a stix_sighting_relationship object (created_by)

        :param id: the id of the stix_sighting_relationship
        :param identity_id: the id of the Identity
        :return Boolean
    """

    def update_created_by(self, **kwargs):
        id = kwargs.get("id", None)
        identity_id = kwargs.get("identity_id", None)
        if id is not None:
            self._api.log(
                "info",
                "Updating author of stix_sighting_relationship {"
                + id
                + "} with Identity {"
                + str(identity_id)
                + "}",
            )
            custom_attributes = """
                id
                createdBy {
                    ... on Identity {
                        id
                        standard_id
                        entity_type
                        parent_types
                        name
                        x_opencti_aliases
                        description
                        created
                        modified
                    }
                    ... on Organization {
                        x_opencti_organization_type
                        x_opencti_reliability
                    }
                    ... on Individual {
                        x_opencti_firstname
                        x_opencti_lastname
                    }
                }
            """
            stix_domain_object = self.read(id=id, customAttributes=custom_attributes)
            if stix_domain_object["createdBy"] is not None:
                query = """
                    mutation StixSightingRelationshipEdit($id: ID!, $toId: String! $relationship_type: String!) {
                        stixSightingRelationshipEdit(id: $id) {
                            relationDelete(toId: $toId, relationship_type: $relationship_type) {
                                id
                            }
                        }
                    }
                """
                self._api.query(
                    query,
                    {
                        "id": id,
                        "toId": stix_domain_object["createdBy"]["id"],
                        "relationship_type": "created-by",
                    },
                )
            if identity_id is not None:
                # Add the new relation
                query = """
                    mutation StixSightingRelationshipEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                        stixSightingRelationshipEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                        }
                    }
               """
                variables = {
                    "id": id,
                    "input": {
                        "toId": identity_id,
                        "relationship_type": "created-by",
                    },
                }
                self._api.query(query, variables)
        else:
            self._api.log("error", "Missing parameters: id")
            return False

    """
        Delete a stix_sighting

        :param id: the stix_sighting id
        :return void
    """

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self._api.log("info", "Deleting stix_sighting {" + id + "}.")
            query = """
                mutation StixSightingRelationshipEdit($id: ID!) {
                    stixSightingRelationshipEdit(id: $id) {
                        delete
                    }
                }
            """
            self._api.query(query, {"id": id})
        else:
            self._api.log("error", "[opencti_stix_sighting] Missing parameters: id")
            return None
