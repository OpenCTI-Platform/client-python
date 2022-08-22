"""OpenCTI ThreatActor operations"""

import json
from typing import Union

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5


class ThreatActor:
    """Threat-Actor domain object"""

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

    def list(self, **kwargs) -> dict:
        """List Threat-Actor objects

        The list method accepts the following kwargs:

        :param list filters: (optional) the filters to apply
        :param str search: (optional) a search keyword to apply for the listing
        :param int first: (optional) return the first n rows from the `after` ID
                            or the beginning if not set
        :param str after: (optional) OpenCTI object ID of the first row for pagination
        :param str orderBy: (optional) the field to order the response on
        :param bool orderMode: (optional) either "`asc`" or "`desc`"
        :param bool getAll: (optional) switch to return all entries (be careful to use this without any other filters)
        :param bool withPagination: (optional) switch to use pagination
        """

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
            "info", "Listing Threat-Actors with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                    query ThreatActors($filters: [ThreatActorsFiltering], $search: String, $first: Int, $after: ID, $orderBy: ThreatActorsOrdering, $orderMode: OrderingMode) {
                        threatActors(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["threatActors"], with_pagination
        )

    def read(self, **kwargs) -> Union[dict, None]:
        """Read a Threat-Actor object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Threat-Actor entity or None.

        The list method accepts the following kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided
        """

        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Threat-Actor {" + id + "}.")
            query = (
                """
                        query ThreatActor($id: String!) {
                            threatActor(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["threatActor"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_threat_actor] Missing parameters: id or filters"
            )
            return None

    def create(self, **kwargs):
        """Create a Threat-Actor object

        The Threat-Actor entity will only be created if it doesn't exists
        By setting `update` to `True` it acts like an upsert and updates
        fields of an existing Threat-Actor entity.

        The create method accepts the following kwargs.

        Note: `name` and `description` or `stix_id` is required.

        :param str stix_id: stix2 id reference for the Threat-Actor entity
        :param str createdBy: (optional) id of the organization that created the knowledge
        :param list objectMarking: (optional) list of OpenCTI markin definition ids
        :param list objectLabel: (optional) list of OpenCTI label ids
        :param list externalReferences: (optional) list of OpenCTI external references ids
        :param bool revoked: is this entity revoked
        :param int confidence: confidence level
        :param str lang: language
        :param str created: (optional) date in OpenCTI date format
        :param str modified: (optional) date in OpenCTI date format
        :param str name: name of the threat actor
        :param str description: description of the threat actor
        :param list aliases: (optional) list of alias names for the Threat-Actor
        :param list threat_actor_types: (optional) list of threat actor types
        :param str first_seen: (optional) date in OpenCTI date format
        :param str last_seen: (optional) date in OpenCTI date format
        :param list roles: (optional) list of roles
        :param list goals: (optional) list of goals
        :param str sophistication: (optional) describe the actors sophistication in text
        :param str resource_level: (optional) describe the actors resource_level in text
        :param str primary_motivation: (optional) describe the actors primary_motivation in text
        :param list secondary_motivations: (optional) describe the actors secondary_motivations in list of string
        :param list personal_motivations: (optional) describe the actors personal_motivations in list of strings
        :param bool update: (optional) choose to updated an existing Threat-Actor entity, default `False`
        """

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
        aliases = kwargs.get("aliases", None)
        threat_actor_types = kwargs.get("threat_actor_types", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        goals = kwargs.get("goals", None)
        sophistication = kwargs.get("sophistication", None)
        resource_level = kwargs.get("resource_level", None)
        primary_motivation = kwargs.get("primary_motivation", None)
        secondary_motivations = kwargs.get("secondary_motivations", None)
        personal_motivations = kwargs.get("personal_motivations", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if name is not None and description is not None:
            self._api.log("info", "Creating Threat-Actor {" + name + "}.")
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
                        "aliases": aliases,
                        "threat_actor_types": threat_actor_types,
                        "first_seen": first_seen,
                        "last_seen": last_seen,
                        "goals": goals,
                        "sophistication": sophistication,
                        "resource_level": resource_level,
                        "primary_motivation": primary_motivation,
                        "secondary_motivations": secondary_motivations,
                        "personal_motivations": personal_motivations,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(result["data"]["threatActorAdd"])
        else:
            self._api.log(
                "error",
                "[opencti_threat_actor] Missing parameters: name and description",
            )

    """
        Import an Threat-Actor object from a STIX2 object

        :param stixObject: the Stix-Object Intrusion-Set
        :return Intrusion-Set object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:

            # Search in extensions
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
        else:
            self._api.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )
