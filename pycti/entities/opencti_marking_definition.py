"""OpenCTI Marking-Definition operations"""

import json

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5

__all__ = [
    "MarkingDefinition",
]


class MarkingDefinition:
    """Marking-Definition common object"""

    def __init__(self, api: OpenCTIApiClient):
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
            definition_type
            definition
            x_opencti_order
            x_opencti_color
            created
            modified
            created_at
            updated_at
        """

    @staticmethod
    def generate_id(definition, definition_type):
        """
        Generate a STIX compliant UUID5.

        :param definition: Marking definition name
        :param definition_type: Marking-definition type ov
        :return: A Stix compliant UUID5
        """

        data = {
            "definition": definition,
            "definition_type": definition_type,
        }

        return _generate_uuid5("marking-definition", data)

    """
        List Marking-Definition objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Marking-Definition objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
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
            "Listing Marking-Definitions with filters " + json.dumps(filters) + ".",
        )
        query = (
            """
                        query MarkingDefinitions($filters: [MarkingDefinitionsFiltering], $first: Int, $after: ID, $orderBy: MarkingDefinitionsOrdering, $orderMode: OrderingMode) {
                            markingDefinitions(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self._api.process_multiple(
            result["data"]["markingDefinitions"], with_pagination
        )

    """
        Read a Marking-Definition object

        :param id: the id of the Marking-Definition
        :param filters: the filters to apply if no id provided
        :return Marking-Definition object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id is not None:
            self._api.log("info", "Reading Marking-Definition {" + id + "}.")
            query = (
                """
                            query MarkingDefinition($id: String!) {
                                markingDefinition(id: $id) {
                                    """
                + self._default_attributes
                + """
                    }
                }
            """
            )
            result = self._api.query(query, {"id": id})
            return self._api.process_multiple_fields(
                result["data"]["markingDefinition"]
            )
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error",
                "[opencti_marking_definition] Missing parameters: id or filters",
            )
            return None

    """
        Create a Marking-Definition object

        :param definition_type: the definition_type
        :param definition: the definition
        :return Marking-Definition object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        definition_type = kwargs.get("definition_type", None)
        definition = kwargs.get("definition", None)
        x_opencti_order = kwargs.get("x_opencti_order", 0)
        x_opencti_color = kwargs.get("x_opencti_color", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if definition is not None and definition_type is not None:
            query = (
                """
                            mutation MarkingDefinitionAdd($input: MarkingDefinitionAddInput) {
                                markingDefinitionAdd(input: $input) {
                                    """
                + self._default_attributes
                + """
                    }
                }
            """
            )
            result = self._api.query(
                query,
                {
                    "input": {
                        "definition_type": definition_type,
                        "definition": definition,
                        "x_opencti_order": x_opencti_order,
                        "x_opencti_color": x_opencti_color,
                        "stix_id": stix_id,
                        "created": created,
                        "modified": modified,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["markingDefinitionAdd"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_marking_definition] Missing parameters: definition and definition_type",
            )

    """
        Update a Marking definition object field

        :param id: the Marking definition id
        :param input: the input of the field
        :return The updated Marking definition object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        if id is not None and input is not None:
            self._api.log("info", "Updating Marking Definition {" + id + "}")
            query = """
                    mutation MarkingDefinitionEdit($id: ID!, $input: [EditInput]!) {
                        markingDefinitionEdit(id: $id) {
                            fieldPatch(input: $input) {
                                id
                                standard_id
                                entity_type
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
                result["data"]["markingDefinitionEdit"]["fieldPatch"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_marking_definition] Missing parameters: id and key and value",
            )
            return None

    """
        Import an Marking Definition object from a STIX2 object

        :param stixObject: the MarkingDefinition
        :return MarkingDefinition object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        update = kwargs.get("update", False)

        if stix_object is not None:
            definition = None
            definition_type = stix_object["definition_type"]
            if stix_object["definition_type"] == "tlp":
                definition_type = definition_type.upper()
                if "definition" in stix_object:
                    definition = (
                        definition_type + ":" + stix_object["definition"]["tlp"].upper()
                    )
                elif "name" in stix_object:
                    definition = stix_object["name"]
            else:
                if "definition" in stix_object:
                    definition = stix_object["definition"][
                        stix_object["definition_type"]
                    ]
                elif "name" in stix_object:
                    definition = stix_object["name"]

            # Search in extensions
            if (
                "x_opencti_order" not in stix_object
                and self._api.get_attribute_in_extension("order", stix_object)
                is not None
            ):
                stix_object["x_opencti_order"] = self._api.get_attribute_in_extension(
                    "order", stix_object
                )
            if "x_opencti_color" not in stix_object:
                stix_object["x_opencti_color"] = self._api.get_attribute_in_extension(
                    "color", stix_object
                )
            if "x_opencti_stix_ids" not in stix_object:
                stix_object[
                    "x_opencti_stix_ids"
                ] = self._api.get_attribute_in_extension("stix_ids", stix_object)

            return self._api.marking_definition.create(
                stix_id=stix_object["id"],
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                definition_type=definition_type,
                definition=definition,
                x_opencti_order=stix_object["x_opencti_order"]
                if "x_opencti_order" in stix_object
                else 0,
                x_opencti_color=stix_object["x_opencti_color"]
                if "x_opencti_color" in stix_object
                else None,
                x_opencti_stix_ids=stix_object["x_opencti_stix_ids"]
                if "x_opencti_stix_ids" in stix_object
                else None,
                update=update,
            )
        else:
            self._api.log(
                "error", "[opencti_marking_definition] Missing parameters: stixObject"
            )

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self._api.log("info", "Deleting Marking-Definition {" + id + "}.")
            query = """
                 mutation MarkingDefinitionEdit($id: ID!) {
                     markingDefinitionEdit(id: $id) {
                         delete
                     }
                 }
             """
            self._api.query(query, {"id": id})
        else:
            self._api.log(
                "error", "[opencti_marking_definition] Missing parameters: id"
            )
            return None
