"""OpenCTI Course-Of-Action operations"""

import json
from typing import TYPE_CHECKING

from . import _generate_uuid5

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "CourseOfAction",
]


class CourseOfAction:
    """Course-Of-Action domain object"""

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
            name
            description
            x_opencti_aliases
            x_mitre_id
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
    def generate_id(name: str, x_mitre_id: str = None) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Course-Of-Action name
        :param x_mitre_id: Mitre ID, if present
        :return: A Stix compliant UUID5
        """

        if x_mitre_id is not None:
            data = {"x_mitre_id": x_mitre_id}
        else:
            data = {"name": name.lower().strip()}

        return _generate_uuid5("course-of-action", data)

    """
        List Course-Of-Action objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Course-Of-Action objects
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
            "info",
            "Listing Course-Of-Actions with filters " + json.dumps(filters) + ".",
        )
        query = (
            """
                    query CoursesOfAction($filters: [CoursesOfActionFiltering], $search: String, $first: Int, $after: ID, $orderBy: CoursesOfActionOrdering, $orderMode: OrderingMode) {
                        coursesOfAction(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["coursesOfAction"], with_pagination
        )

    """
        Read a Course-Of-Action object

        :param id: the id of the Course-Of-Action
        :param filters: the filters to apply if no id provided
        :return Course-Of-Action object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Course-Of-Action {" + id + "}.")
            query = (
                """
                        query CourseOfAction($id: String!) {
                            courseOfAction(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["courseOfAction"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_course_of_action] Missing parameters: id or filters"
            )
            return None

    """
        Create a Course Of Action object

        :param name: the name of the Course Of Action
        :return Course Of Action object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        x_mitre_id = kwargs.get("x_mitre_id", None)
        update = kwargs.get("update", False)

        if name is not None and description is not None:
            self._api.log("info", "Creating Course Of Action {" + name + "}.")
            query = """
                mutation CourseOfActionAdd($input: CourseOfActionAddInput) {
                    courseOfActionAdd(input: $input) {
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
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "name": name,
                        "description": description,
                        "x_opencti_aliases": x_opencti_aliases,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "x_mitre_id": x_mitre_id,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["courseOfActionAdd"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_course_of_action] Missing parameters: name and description",
            )

    """
        Import an Course-Of-Action object from a STIX2 object

        :param stixObject: the Stix-Object Course-Of-Action
        :return Course-Of-Action object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            # Extract external ID
            x_mitre_id = None
            if "x_mitre_id" in stix_object:
                x_mitre_id = stix_object["x_mitre_id"]
            elif (
                self._api.get_attribute_in_mitre_extension("id", stix_object)
                is not None
            ):
                x_mitre_id = self._api.get_attribute_in_mitre_extension(
                    "id", stix_object
                )
            elif "external_references" in stix_object:
                for external_reference in stix_object["external_references"]:
                    if (
                        external_reference["source_name"] == "mitre-attack"
                        or external_reference["source_name"] == "mitre-pre-attack"
                        or external_reference["source_name"] == "mitre-mobile-attack"
                        or external_reference["source_name"] == "amitt-attack"
                    ):
                        x_mitre_id = external_reference["external_id"]

            # Search in extensions
            if "x_opencti_aliases" not in stix_object:
                stix_object["x_opencti_aliases"] = self._api.get_attribute_in_extension(
                    "aliases", stix_object
                )
            if "x_opencti_stix_ids" not in stix_object:
                stix_object[
                    "x_opencti_stix_ids"
                ] = self._api.get_attribute_in_extension("stix_ids", stix_object)

            return self.create(
                stix_id=stix_object["id"],
                createdBy=extras.get("created_by_id"),
                objectMarking=extras.get("object_marking_ids"),
                objectLabel=extras.get("object_label_ids", []),
                externalReferences=extras.get("external_references_ids", []),
                revoked=stix_object.get("revoked"),
                confidence=stix_object.get("confidence"),
                lang=stix_object.get("lang"),
                created=stix_object.get("created"),
                modified=stix_object.get("modified"),
                name=stix_object["name"],
                description=self._api.stix2.convert_markdown(stix_object["description"])
                if "description" in stix_object
                else "",
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                x_opencti_aliases=self._api.stix2.pick_aliases(stix_object),
                x_mitre_id=x_mitre_id,
                update=update,
            )
        else:
            self._api.log(
                "error", "[opencti_course_of_action] Missing parameters: stixObject"
            )
