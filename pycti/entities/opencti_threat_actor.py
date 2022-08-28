"""OpenCTI ThreatActor operations"""

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
from .models.opencti_common import OrderingMode
from .models.opencti_threat_actor import (
    ImportThreatActorExtras,
    ThreatActorFiltering,
    ThreatActorOrdering,
)

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "ThreatActor",
]

log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]


class ThreatActor:
    """Threat-Actor domain object"""

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
            threat_actor_types
            first_seen
            last_seen
            roles
            goals
            sophistication
            resource_level
            primary_motivation
            secondary_motivations
            personal_motivations
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

        :param name: Threat-Actor name
        :return: A Stix compliant UUID5
        """

        data = {"name": name.lower().strip()}
        return _generate_uuid5("threat-actor", data)

    def list(
        self,
        *,
        filters: List[ThreatActorFiltering] = None,
        search: str = None,
        first: int = 500,
        after: str = None,
        order_by: ThreatActorOrdering = None,
        order_mode: OrderingMode = None,
        attributes: str = None,
        get_all: bool = False,
        with_pagination: bool = False,
        **kwargs: Any,
    ) -> Union[AnyDict, List[AnyDict]]:
        """
        List Threat-Actor objects.

        :param filters: Filters to search by
        :param search: Search value, an arbitrary string
        :param first: Fetch the first N rows from the after ID, or the beginning if not set
        :param after: ID of the first row for pagination
        :param order_by: The field to order by
        :param order_mode: The ordering mode
        :param attributes: Customize the GraphQL attributes returned
        :param get_all: Get all existing objects
        :param with_pagination: Get the first page, with the pagination fields
        :return A list of Threat-Actor objects
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

        log.info("Listing Threat-Actors with filters %s.", json.dumps(filters))
        query = """
            query ThreatActors($filters: [ThreatActorsFiltering], $search: String, $first: Int, $after: ID, $orderBy: ThreatActorsOrdering, $orderMode: OrderingMode) {
                threatActors(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                    log.info("Listing Threat-Actors after %s", after)

                result = self._api.query(query, variables)

                connection = result["data"]["threatActors"]
                data = self._api.process_multiple(connection)
                final_data += data

                pageinfo = connection["pageInfo"]
                after = variables["after"] = pageinfo["endCursor"]
                has_more = pageinfo["hasNextPage"]
            return final_data

        else:
            result = self._api.query(query, variables)
            connection = result["data"]["threatActors"]
            return self._api.process_multiple(connection, with_pagination)

    def read(
        self,
        *,
        id: str = None,
        filters: List[ThreatActorFiltering] = None,
        attributes: str = None,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Read a Threat-Actor object.

        :param id: The ID of a Threat-Actor
        :param filters: Filters to search by if no ID is provided
        :param attributes: Customize the GraphQL attributes returned
        :return: A Threat-Actor object or None
        """

        if kwargs:
            attributes = _check_for_deprecated_parameter(
                "customAttributes", "attributes", attributes, kwargs
            )
            _check_for_excess_parameters(kwargs)

        if attributes is None:
            attributes = self._default_attributes

        if id is not None:
            log.info("Reading Threat-Actor {%s}", id)
            query = """
                query ThreatActor($id: String!) {
                    threatActor(id: $id) {
                        %s
                    }
                }
            """
            query %= attributes
            variables = {"id": id}
            result = self._api.query(query, variables)
            entity = result["data"]["threatActor"]
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
        stix_id: str = None,
        x_opencti_stix_ids: List[str] = None,
        name: str = None,
        description: str = None,
        aliases: List[str] = None,
        threat_actor_types: [str] = None,
        first_seen: datetime = None,
        last_seen: datetime = None,
        # roles: List[str] = None, # TODO This was missing before
        goals: List[str] = None,
        sophistication: str = None,
        resource_level: str = None,
        primary_motivation: str = None,
        secondary_motivations: List[str] = None,
        personal_motivations: List[str] = None,
        confidence: int = None,
        revoked: bool = None,
        lang: str = None,
        created_by: str = None,
        object_marking: List[str] = None,
        object_label: List[str] = None,
        external_references: List[str] = None,
        created: datetime = None,
        modified: datetime = None,
        update: bool = False,
        **kwargs: Any,
    ):
        """
        Create a Threat-Actor object.

        :return: A Threat-Actor object
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
            _check_for_excess_parameters(kwargs)

        if name is None:
            # TODO throw?
            log.error("Missing parameter: name")
            return None

        if description is None:
            # TODO throw?
            log.error("Missing parameter: description")
            return None

        log.info("Creating Threat-Actor {%s}.", name)
        query = """
            mutation ThreatActorAdd($input: ThreatActorAddInput) {
                threatActorAdd(input: $input) {
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
                "threat_actor_types": threat_actor_types,
                "first_seen": first_seen,
                "last_seen": last_seen,
                # "roles": roles,  # TODO this was missing before
                "goals": goals,
                "sophistication": sophistication,
                "resource_level": resource_level,
                "primary_motivation": primary_motivation,
                "secondary_motivations": secondary_motivations,
                "personal_motivations": personal_motivations,
                "x_opencti_stix_ids": x_opencti_stix_ids,
                "update": update,
            }
        }
        result = self._api.query(query, variables)
        entity = result["data"]["threatActorAdd"]
        return self._api.process_multiple_fields(entity)

    def import_from_stix2(
        self,
        *,
        stix_object: stix2.ThreatActor = None,
        extras: ImportThreatActorExtras = None,
        update: bool = False,
        **kwargs: Any,
    ) -> Optional[AnyDict]:
        """
        Import a stix2.ThreatActor object.

        :param stix_object: A STIX object
        :param extras: Extra OpenCTI fields
        :param update: Update existing data
        :return: A Threat-Actor object
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
            description=description,
            aliases=self._api.stix2.pick_aliases(stix_object),
            threat_actor_types=stix_object.get("threat_actor_types"),
            first_seen=stix_object.get("first_seen"),
            last_seen=stix_object.get("last_seen"),
            goals=stix_object.get("goals"),
            sophistication=stix_object.get("sophistication"),
            resource_level=stix_object.get("resource_level"),
            primary_motivation=stix_object.get("primary_motivation"),
            secondary_motivations=stix_object.get("secondary_motivations"),
            personal_motivations=stix_object.get("personal_motivations"),
            x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
            update=update,
        )
