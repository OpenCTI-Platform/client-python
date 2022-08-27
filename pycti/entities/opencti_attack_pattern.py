"""OpenCTI Attack-Pattern operations"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import stix2

from . import (
    _check_for_deprecated_parameter,
    _check_for_excess_parameters,
    _generate_uuid5,
)
from .models.opencti_attack_pattern import (
    AttackPatternFiltering,
    AttackPatternOrdering,
    ImportAttackPatternExtras,
)
from .models.opencti_common import OrderingMode

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


__all__ = [
    "AttackPattern",
]

log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]


class AttackPattern:
    """Attack-Pattern domain object"""

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
            aliases
            x_mitre_platforms
            x_mitre_permissions_required
            x_mitre_detection
            x_mitre_id
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
    def generate_id(name: str, x_mitre_id: str = None) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Attack-Pattern name
        :param x_mitre_id: Mitre ID, if present
        :return: A Stix compliant UUID5
        """

        if x_mitre_id is not None:
            data = {"x_mitre_id": x_mitre_id}
        else:
            data = {"name": name.lower().strip()}

        return _generate_uuid5("attack-pattern", data)

    def list(
        self,
        *,
        filters: List[AttackPatternFiltering] = None,
        search: str = None,
        first: int = 500,
        after: str = None,
        order_by: AttackPatternOrdering = None,
        order_mode: OrderingMode = None,
        attributes: str = None,
        get_all: bool = False,
        with_pagination: bool = False,
        **kwargs: Any,
    ) -> Union[AnyDict, List[AnyDict]]:
        """
        List Attack-Pattern objects.

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
            first = 500
        if attributes is None:
            attributes = self._default_attributes

        log.info("Listing Attack-Patterns with filters %s", json.dumps(filters))

        query = """
            query AttackPatterns($filters: [AttackPatternsFiltering], $search: String, $first: Int, $after: ID, $orderBy: AttackPatternsOrdering, $orderMode: OrderingMode) {
                attackPatterns(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                    log.info("Listing Attack-Patterns after %s", after)

                result = self._api.query(query, variables)

                connection = result["data"]["attackPatterns"]
                data = self._api.process_multiple(connection)
                final_data += data

                pageinfo = connection["pageInfo"]
                after = variables["after"] = pageinfo["endCursor"]
                has_more = pageinfo["hasNextPage"]
            return final_data

        else:
            result = self._api.query(query, variables)
            connection = result["data"]["attackPatterns"]
            return self._api.process_multiple(connection, with_pagination)

    def read(
        self,
        *,
        id: str = None,
        filters: List[AttackPatternFiltering] = None,
        attributes: str = None,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Read an Attack-Pattern object.

        :param id: The ID of an Attack-Pattern
        :param filters: Filters to search by if no ID is provided
        :param attributes: Customize the GraphQL attributes returned
        :return: An Attack-Pattern object or None
        """

        if kwargs:
            attributes = _check_for_deprecated_parameter(
                "customAttributes", "attributes", attributes, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if attributes is None:
            attributes = self._default_attributes

        if id is not None:
            log.info("Reading Attack-Pattern {%s}", id)
            query = """
                query AttackPattern($id: String!) {
                    attackPattern(id: $id) {
                        %s
                    }
                }
            """
            query %= attributes
            variables = {"id": id}
            result = self._api.query(query, variables)
            entity = result["data"]["attackPattern"]
            return self._api.process_multiple_fields(entity)

        elif filters is not None:
            result = self.list(filters=filters)
            return next(iter(result), None)

        else:
            # TODO throw?
            log.error("Missing parameter: id or filters")
            return None

    def create(
        self,
        *,
        name: str = None,
        stix_id: str = None,
        x_opencti_stix_ids: List[str] = None,
        created_by: str = None,
        object_marking: List[str] = None,
        object_label: List[str] = None,
        external_references: List[str] = None,
        revoked: bool = None,
        confidence: int = None,
        lang: str = None,
        created: datetime = None,
        modified: datetime = None,
        description: str = None,
        aliases: List[str] = None,
        x_mitre_platforms: List[str] = None,
        x_mitre_permissions_required: List[str] = None,
        x_mitre_detection: str = None,
        x_mitre_id: str = None,
        kill_chain_phases: List[str] = None,
        update: bool = False,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Create an Attack-Pattern object.

        :return: An Attack-Pattern object
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

        if name is not None:
            # TODO throw?
            log.error("Missing parameter: name")
            return None

        log.info("Creating Attack-Pattern {%s}", name)
        query = """
            mutation AttackPatternAdd($input: AttackPatternAddInput) {
                attackPatternAdd(input: $input) {
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
                "x_mitre_platforms": x_mitre_platforms,
                "x_mitre_permissions_required": x_mitre_permissions_required,
                "x_mitre_detection": x_mitre_detection,
                "x_mitre_id": x_mitre_id,
                "killChainPhases": kill_chain_phases,
                "x_opencti_stix_ids": x_opencti_stix_ids,
                "update": update,
            }
        }
        result = self._api.query(query, variables)
        entity = result["data"]["attackPatternAdd"]
        return self._api.process_multiple_fields(entity)

    def import_from_stix2(
        self,
        *,
        stix_object: stix2.AttackPattern = None,
        extras: ImportAttackPatternExtras = None,
        update: bool = False,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Import a stix2.AttackPattern object.

        :param stix_object: A STIX object
        :param extras: Extra OpenCTI fields
        :param update: Update existing data
        :return: An Attack-Pattern object
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

        # Extract external ID
        x_mitre_id = stix_object.get("x_mitre_id")
        if x_mitre_id is None:
            x_mitre_id = self._api.get_attribute_in_mitre_extension("id", stix_object)
        if x_mitre_id is None:
            refs = stix_object.get("external_references") or []
            names = [
                "mitre-attack",
                "mitre-pre-attack",
                "mitre-mobile-attack",
                "mitre-ics-attack",
                "amitt-attack",
            ]
            for external_reference in refs:
                if external_reference["source_name"] in names:
                    x_mitre_id = external_reference.get("external_id")

        # Search in extensions
        if "x_opencti_order" not in stix_object:
            value = self._api.get_attribute_in_extension("order", stix_object)
            stix_object["x_opencti_order"] = value or 0

        if "x_mitre_platforms" not in stix_object:
            value = self._api.get_attribute_in_mitre_extension("platforms", stix_object)
            stix_object["x_mitre_platforms"] = value

        if "x_mitre_permissions_required" not in stix_object:
            value = self._api.get_attribute_in_mitre_extension(
                "permissions_required", stix_object
            )
            stix_object["x_mitre_permissions_required"] = value

        if "x_mitre_detection" not in stix_object:
            value = self._api.get_attribute_in_mitre_extension("detection", stix_object)
            stix_object["x_mitre_detection"] = value

        if "x_opencti_stix_ids" not in stix_object:
            value = self._api.get_attribute_in_extension("stix_ids", stix_object)
            stix_object["x_opencti_stix_ids"] = value

        description = stix_object.get("description") or ""
        if description:
            description = self._api.stix2.convert_markdown(description)

        x_mitre_platforms = stix_object.get("x_mitre_platforms")
        if not x_mitre_platforms:
            x_mitre_platforms = stix_object.get("x_amitt_platforms")

        return self.create(
            stix_id=stix_object["id"],
            name=stix_object["name"],
            created_by=extras.get("created_by_id"),
            object_marking=extras.get("object_marking_ids"),
            object_label=extras.get("object_label_ids", []),
            external_references=extras.get("external_references_ids", []),
            kill_chain_phases=extras.get("kill_chain_phases_ids"),
            revoked=stix_object.get("revoked", None),
            confidence=stix_object.get("confidence"),
            lang=stix_object.get("lang"),
            created=stix_object.get("created"),
            modified=stix_object.get("modified"),
            description=description,
            aliases=self._api.stix2.pick_aliases(stix_object),
            x_mitre_platforms=x_mitre_platforms,
            x_mitre_permissions_required=stix_object.get(
                "x_mitre_permissions_required"
            ),
            x_mitre_detection=stix_object.get("x_mitre_detection"),
            x_mitre_id=x_mitre_id,
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
        Delete an Attack-Pattern object.

        :param id: The ID of an Attack-Pattern
        :return: None
        """

        _check_for_excess_parameters(kwargs)

        if id is None:
            # TODO throw?
            log.error("Missing parameter: id")
            return

        log.info("Deleting Attack Pattern {%s}.", id)
        query = """
             mutation AttackPatternEdit($id: ID!) {
                 attackPatternEdit(id: $id) {
                     delete
                 }
             }
         """
        variables = {"id": id}
        self._api.query(query, variables)
