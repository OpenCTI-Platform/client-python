"""OpenCTI Tool operations"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import stix2

from ..api.opencti_api_client import OpenCTIApiClient
from . import (
    _check_for_deprecated_parameter,
    _check_for_excess_parameters,
    _generate_uuid5,
)
from .models.opencti_common import OrderingMode
from .models.opencti_tool import ImportToolExtras, ToolFiltering, ToolOrdering

__all__ = [
    "Tool",
]

log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]


class Tool:
    """Tool domain object"""

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
            aliases
            tool_types
            tool_version
            killChainPhases {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        kill_chain_name
                        phase_name
                        x_opencti_order
                        created
                        modified
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
    def generate_id(name: str) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Vulnerability name
        :return: A Stix compliant UUID5
        """

        data = {"name": name.lower().strip()}
        return _generate_uuid5("tool", data)

    def list(
        self,
        *,
        filters: List[ToolFiltering] = None,
        search: str = None,
        first: int = 100,
        after: str = None,
        order_by: ToolOrdering = None,
        order_mode: OrderingMode = None,
        attributes: str = None,
        get_all: bool = False,
        with_pagination: bool = False,
        **kwargs: Any,
    ) -> Union[AnyDict, List[AnyDict]]:
        """
        List Tool objects.

        :param filters: Filters to search by
        :param search: Search value, an arbitrary string
        :param first: Fetch the first N rows from the after ID, or the beginning if not set
        :param after: ID of the first row for pagination
        :param order_by: The field to order by
        :param order_mode: The ordering mode
        :param attributes: Customize the GraphQL attributes returned
        :param get_all: Get all existing objects
        :param with_pagination: Get the first page, with the pagination fields
        :return A list of Attack-Pattern objects
        """

        if kwargs:
            order_by = _check_for_deprecated_parameter(
                "orderBy", "order_by", order_by, kwargs
            )
            order_mode = _check_for_deprecated_parameter(
                "orderMode", "order_mode", order_mode, kwargs
            )
            attributes = _check_for_deprecated_parameter(
                "customAttributes", "attributes", attributes, kwargs
            )
            with_pagination = _check_for_deprecated_parameter(
                "withPagination", "with_pagination", with_pagination, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if get_all:
            first = 100
        if attributes is None:
            attributes = self._default_attributes

        log.info("Listing Tools with filters %s.", json.dumps(filters))
        query = """
            query Tools($filters: [ToolsFiltering], $search: String, $first: Int, $after: ID, $orderBy: ToolsOrdering, $orderMode: OrderingMode) {
                tools(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            %s
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
        query %= attributes
        variables = {
            "filters": filters,
            "search": search,
            "first": first,
            "after": after,
            "orderBy": order_by,
            "orderMode": order_mode,
        }

        if get_all:
            has_more = True
            final_data = []
            while has_more:
                if after:
                    log.info("Listing Tools after %s", after)

                result = self._api.query(query, variables)

                connection = result["data"]["tools"]
                data = self._api.process_multiple(connection)
                final_data += data

                pageinfo = connection["pageInfo"]
                after = variables["after"] = pageinfo["endCursor"]
                has_more = pageinfo["hasNextPage"]
            return final_data

        else:
            result = self._api.query(query, variables)
            connection = result["data"]["tools"]
            return self._api.process_multiple(connection, with_pagination)

    def read(
        self,
        *,
        id: str = None,
        filters: List[ToolFiltering] = None,
        attributes: str = None,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Read a Tool object.

        :param id: The ID of a Tool
        :param filters: Filters to search by if no ID is provided
        :param attributes: Customize the GraphQL attributes returned
        :return: A Tool object or None
        """

        if kwargs:
            attributes = _check_for_deprecated_parameter(
                "customAttributes", "attributes", attributes, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if attributes is None:
            attributes = self._default_attributes

        if id is not None:
            log.info("Reading Tool {%s}.", id)
            query = """
                query Tool($id: String!) {
                    tool(id: $id) {
                        %s            
                    }
                }
            """
            query %= attributes
            variables = {"id": id}
            result = self._api.query(query, variables)
            entity = result["data"]["tool"]
            return self._api.process_multiple_fields(entity)

        elif filters is not None:
            result = self.list(filters=filters)
            return next(iter(result), None)

        else:
            # TODO throw?
            log.error("Missing parameters: id or filters")
            return None

    def create(
        self,
        *,
        stix_id: str = None,
        x_opencti_stix_ids: List[str] = None,
        name: str = None,
        description: str = "",
        aliases: List[str] = None,
        tool_types: List[str] = None,
        tool_version: str = None,
        confidence: int = None,
        revoked: bool = None,
        lang: str = None,
        created_by: str = None,
        object_marking: List[str] = None,
        object_label: List[str] = None,
        external_references: List[str] = None,
        kill_chain_phases: List[str] = None,
        created: datetime = None,
        modified: datetime = None,
        update: bool = False,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Create a Tool object.

        :return: A Tool object
        """

        if kwargs:
            created_by = _check_for_deprecated_parameter(
                "createdBy", "created_by", created_by, kwargs
            )
            object_marking = _check_for_deprecated_parameter(
                "objectMarking", "object_marking", object_marking, kwargs
            )
            object_label = _check_for_deprecated_parameter(
                "objectLabel", "object_label", object_label, kwargs
            )
            external_references = _check_for_deprecated_parameter(
                "externalReferences", "external_references", external_references, kwargs
            )
            kill_chain_phases = _check_for_deprecated_parameter(
                "killChainPhases", "kill_chain_phases", kill_chain_phases, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if name is None:
            # TODO throw? also description is not required per stix2?
            log.error("Missing parameter: name")
            return None

        log.info("Creating Tool {%s}.", name)
        query = """
            mutation ToolAdd($input: ToolAddInput) {
                toolAdd(input: $input) {
                    id
                    standard_id
                    entity_type
                    parent_types
                }
            }
        """
        variables = {
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
                "aliases": aliases,
                "tool_types": tool_types,
                "tool_version": tool_version,
                "killChainPhases": kill_chain_phases,
                "x_opencti_stix_ids": x_opencti_stix_ids,
                "update": update,
            }
        }
        result = self._api.query(query, variables)
        entity = result["data"]["toolAdd"]
        return self._api.process_multiple_fields(entity)

    def import_from_stix2(
        self,
        *,
        stix_object: stix2.Tool = None,
        extras: ImportToolExtras = None,
        update: bool = False,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Import a stix2.Tool object.

        :param stix_object: A STIX object
        :param extras: Extra OpenCTI fields
        :param update: Update existing data
        :return: A Tool object
        """

        if kwargs:
            stix_object = _check_for_deprecated_parameter(
                "stixObject", "stix_object", stix_object, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if extras is None:
            extras = {}

        if stix_object is None:
            # TODO throw?
            log.error("Missing parameter: stix_object")
            return None

        # Search in extensions
        if "x_opencti_stix_ids" not in stix_object:
            value = self._api.get_attribute_in_extension("stix_ids", stix_object)
            stix_object["x_opencti_stix_ids"] = value

        description = stix_object.get("description") or ""
        if description:
            description = self._api.stix2.convert_markdown(description)

        return self._api.tool.create(
            stix_id=stix_object["id"],
            created_by=extras.get("created_by_id"),
            object_marking=extras.get("object_marking_ids"),
            object_label=extras.get("object_label_ids", []),
            external_references=extras.get("external_references_ids", []),
            revoked=stix_object.get("revoked"),
            confidence=stix_object.get("confidence"),
            lang=stix_object.get("lang"),
            created=stix_object.get("created"),
            modified=stix_object.get("modified"),
            name=stix_object["name"],
            description=description,
            aliases=self._api.stix2.pick_aliases(stix_object),
            tool_types=stix_object.get("tool_types"),
            tool_version=stix_object.get("tool_version"),
            kill_chain_phases=extras.get("kill_chain_phases_ids"),
            x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
            update=update,
        )

    def delete(
        self,
        *,
        id: str = None,
        **kwargs: Any,
    ) -> None:
        """
        Delete a Tool object.

        :param id: The ID of a Tool
        :return: None
        """

        _check_for_excess_parameters(kwargs)

        if id is None:
            # TODO throw?
            log.error("Missing parameter: id")
            return

        log.info("Deleting Tool {%s}.", id)
        query = """
             mutation ToolEdit($id: ID!) {
                 toolEdit(id: $id) {
                     delete
                 }
             }
         """
        variables = {"id": id}
        self._api.query(query, variables)
