"""OpenCTI Infrastructure operations"""

import json

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5

__all__ = [
    "Infrastructure",
]


class Infrastructure:
    """Infrastructure domain object"""

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
            infrastructure_types
            first_seen
            last_seen
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

        :param name: Infrastructure name
        :return: A Stix compliant UUID5
        """

        data = {"name": name.lower().strip()}
        return _generate_uuid5("infrastructure", data)

    def list(self, **kwargs):
        """List Infrastructure objects

        The list method accepts the following kwargs:

        :param list filters: (optional) the filters to apply
        :param str search: (optional) a search keyword to apply for the listing
        :param int first: (optional) return the first n rows from the `after` ID
                            or the beginning if not set
        :param str after: (optional) OpenCTI object ID of the first row for pagination
        :param str orderBy: (optional) the field to order the response on
        :param bool orderMode: (optional) either "`asc`" or "`desc`"
        :param list customAttributes: (optional) list of attributes keys to return
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
            "info", "Listing Infrastructures with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                    query Infrastructures($filters: [InfrastructuresFiltering], $search: String, $first: Int, $after: ID, $orderBy: InfrastructuresOrdering, $orderMode: OrderingMode) {
                        infrastructures(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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

        if get_all:
            final_data = []
            data = self._api.process_multiple(result["data"]["infrastructures"])
            final_data = final_data + data
            while result["data"]["infrastructures"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["infrastructures"]["pageInfo"]["endCursor"]
                self._api.log("info", "Listing Infrastructures after " + after)
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
                data = self._api.process_multiple(result["data"]["infrastructures"])
                final_data = final_data + data
            return final_data
        else:
            return self._api.process_multiple(
                result["data"]["infrastructures"], with_pagination
            )

    def read(self, **kwargs):
        """Read an Infrastructure object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Infrastructure entity or None.

        The list method accepts the following kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided
        """

        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Infrastructure {" + id + "}.")
            query = (
                """
                        query Infrastructure($id: String!) {
                            infrastructure(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["infrastructure"])
        elif filters is not None:
            result = self.list(filters=filters, customAttributes=custom_attributes)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_infrastructure] Missing parameters: id or filters"
            )
            return None

    """
        Create a Infrastructure object

        :param name: the name of the Infrastructure
        :return Infrastructure object
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
        description = kwargs.get("description", None)
        aliases = kwargs.get("aliases", None)
        infrastructure_types = kwargs.get("infrastructure_types", None)
        first_seen = kwargs.get("first_seen", None)
        last_seen = kwargs.get("last_seen", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if name is not None:
            self._api.log("info", "Creating Infrastructure {" + name + "}.")
            query = """
                mutation InfrastructureAdd($input: InfrastructureAddInput) {
                    infrastructureAdd(input: $input) {
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
                        "infrastructure_types": infrastructure_types,
                        "first_seen": first_seen,
                        "last_seen": last_seen,
                        "killChainPhases": kill_chain_phases,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(
                result["data"]["infrastructureAdd"]
            )
        else:
            self._api.log(
                "error",
                "[opencti_infrastructure] Missing parameters: name and infrastructure_pattern and main_observable_type",
            )

    """
        Import an Infrastructure object from a STIX2 object

        :param stixObject: the Stix-Object Infrastructure
        :return Infrastructure object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)

        # Search in extensions
        if "x_opencti_stix_ids" not in stix_object:
            stix_object["x_opencti_stix_ids"] = self._api.get_attribute_in_extension(
                "stix_ids", stix_object
            )

        if stix_object is not None:
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
                infrastructure_types=stix_object.get("infrastructure_types"),
                first_seen=stix_object.get("first_seen"),
                last_seen=stix_object.get("last_seen"),
                killChainPhases=extras.get("kill_chain_phases_ids"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                update=update,
            )
        else:
            self._api.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )
