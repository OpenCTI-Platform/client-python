"""OpenCTI Observed-Data operations"""

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List

from . import _generate_uuid5

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "ObservedData",
]

log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]


class ObservedData:
    """Observed-Data domain object"""

    def __init__(self, api: "OpenCTIApiClient"):
        """
        Constructor.

        :param api: OpenCTI API client
        """

        self._api = api
        self._default_attributes = """
            id
            standard_id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    spec_version
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
                        importFiles {
                            edges {
                                node {
                                    id
                                    name
                                    size
                                    metaData {
                                        mimetype
                                        version
                                    }
                                }
                            }
                        }
                    }
                }
            }
            revoked
            confidence
            created
            modified
            first_observed
            last_observed
            number_observed
            objects {
                edges {
                    node {
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
                        ... on StixCoreRelationship {
                            standard_id
                            spec_version
                            created_at
                            updated_at
                        }
                    }
                }
            }
            importFiles {
                edges {
                    node {
                        id
                        name
                        size
                        metaData {
                            mimetype
                            version
                        }
                    }
                }
            }
        """

    @staticmethod
    def generate_id(object_ids: List[str]) -> str:
        """
        Generate a STIX compliant UUID5.

        :param object_ids: Object IDs
        :return: A Stix compliant UUID5
        """

        data = {"objects": object_ids}
        return _generate_uuid5("observed-data", data)

    """
        List ObservedData objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of ObservedData objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 500

        self._api.log(
            "info", "Listing ObservedDatas with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                query ObservedDatas($filters: [ObservedDatasFiltering], $search: String, $first: Int, $after: ID, $orderBy: ObservedDatasOrdering, $orderMode: OrderingMode) {
                    observedDatas(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self._api.process_multiple(
            result["data"]["observedDatas"], with_pagination
        )

    """
        Read a ObservedData object

        :param id: the id of the ObservedData
        :param filters: the filters to apply if no id provided
        :return ObservedData object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading ObservedData {" + id + "}.")
            query = (
                """
                    query ObservedData($id: String!) {
                        observedData(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["observedData"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Check if a observedData already contains a STIX entity

        :return Boolean
    """

    def contains_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self._api.log(
                "info",
                "Checking StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} in ObservedData {"
                + id
                + "}",
            )
            query = """
                query ObservedDataContainsStixObjectOrStixRelationship($id: String!, $stixObjectOrStixRelationshipId: String!) {
                    observedDataContainsStixObjectOrStixRelationship(id: $id, stixObjectOrStixRelationshipId: $stixObjectOrStixRelationshipId)
                }
            """
            result = self._api.query(
                query,
                {
                    "id": id,
                    "stixObjectOrStixRelationshipId": stix_object_or_stix_relationship_id,
                },
            )
            return result["data"]["observedDataContainsStixObjectOrStixRelationship"]
        else:
            self._api.log(
                "error",
                "[opencti_observedData] Missing parameters: id or entity_id",
            )

    """
        Create a ObservedData object

        :param name: the name of the ObservedData
        :return ObservedData object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        objects = kwargs.get("objects", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        first_observed = kwargs.get("first_observed", None)
        last_observed = kwargs.get("last_observed", None)
        number_observed = kwargs.get("number_observed", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if (
            first_observed is not None
            and last_observed is not None
            and objects is not None
        ):
            self._api.log("info", "Creating ObservedData.")
            query = """
                mutation ObservedDataAdd($input: ObservedDataAddInput) {
                    observedDataAdd(input: $input) {
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
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": object_marking,
                        "objectLabel": object_label,
                        "objects": objects,
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "first_observed": first_observed,
                        "last_observed": last_observed,
                        "number_observed": number_observed,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(result["data"]["observedDataAdd"])
        else:
            self._api.log(
                "error",
                "[opencti_observedData] Missing parameters: first_observed, last_observed or objects",
            )

    """
        Add a Stix-Core-Object or stix_relationship to ObservedData object (object)

        :param id: the id of the ObservedData
        :param entity_id: the id of the Stix-Core-Object or stix_relationship
        :return Boolean
    """

    def add_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            if self.contains_stix_object_or_stix_relationship(
                id=id,
                stixObjectOrStixRelationshipId=stix_object_or_stix_relationship_id,
            ):
                return True
            self._api.log(
                "info",
                "Adding StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} to ObservedData {"
                + id
                + "}",
            )
            query = """
               mutation ObservedDataEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                   observedDataEdit(id: $id) {
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
                        "toId": stix_object_or_stix_relationship_id,
                        "relationship_type": "object",
                    },
                },
            )
            return True
        else:
            self._api.log(
                "error",
                "[opencti_observedData] Missing parameters: id and stix_object_or_stix_relationship_id",
            )
            return False

    """
        Remove a Stix-Core-Object or stix_relationship to Observed-Data object (object_refs)

        :param id: the id of the Observed-Data
        :param entity_id: the id of the Stix-Core-Object or stix_relationship
        :return Boolean
    """

    def remove_stix_object_or_stix_relationship(self, **kwargs):
        id = kwargs.get("id", None)
        stix_object_or_stix_relationship_id = kwargs.get(
            "stixObjectOrStixRelationshipId", None
        )
        if id is not None and stix_object_or_stix_relationship_id is not None:
            self._api.log(
                "info",
                "Removing StixObjectOrStixRelationship {"
                + stix_object_or_stix_relationship_id
                + "} to Observed-Data {"
                + id
                + "}",
            )
            query = """
               mutation ObservedDataEditRelationDelete($id: ID!, $toId: String!, $relationship_type: String!) {
                   observedDataEdit(id: $id) {
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
                    "toId": stix_object_or_stix_relationship_id,
                    "relationship_type": "object",
                },
            )
            return True
        else:
            self._api.log(
                "error", "[opencti_observed_data] Missing parameters: id and entity_id"
            )
            return False

    """
        Import a ObservedData object from a STIX2 object

        :param stixObject: the Stix-Object ObservedData
        :return ObservedData object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        object_refs = extras["object_ids"] if "object_ids" in extras else []

        if "objects" in stix_object:
            stix_observable_results = []
            for key, observable_item in stix_object["objects"].items():
                stix_observable_results.append(
                    self._api.stix_cyber_observable.create(
                        observableData=observable_item,
                        createdBy=extras.get("created_by_id"),
                        objectMarking=extras.get("object_marking_ids"),
                        objectLabel=extras.get("object_label_ids", []),
                    )
                )
                for item in stix_observable_results:
                    object_refs.append(item["standard_id"])

        if stix_object is not None:

            # Search in extensions
            if "x_opencti_stix_ids" not in stix_object:
                stix_object[
                    "x_opencti_stix_ids"
                ] = self._api.get_attribute_in_extension("stix_ids", stix_object)

            observed_data_result = self.create(
                stix_id=stix_object["id"],
                createdBy=extras.get("created_by_id"),
                objectMarking=extras.get("object_marking_ids"),
                objectLabel=extras.get("object_label_ids", []),
                objects=object_refs,
                externalReferences=extras.get("external_references_ids", []),
                revoked=stix_object.get("revoked"),
                confidence=stix_object.get("confidence"),
                lang=stix_object.get("lang"),
                created=stix_object.get("created"),
                modified=stix_object.get("modified"),
                first_observed=stix_object.get("first_observed"),
                last_observed=stix_object.get("last_observed"),
                number_observed=stix_object.get("number_observed"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                update=update,
            )

            return observed_data_result
        else:
            self._api.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )
