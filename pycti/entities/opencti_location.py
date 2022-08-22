"""OpenCTI Location operations"""

import json

from ..api.opencti_api_client import OpenCTIApiClient
from . import _generate_uuid5

__all__ = [
    "Location",
]


class Location:
    """Location domain object"""

    def __init__(self, api: OpenCTIApiClient):
        """
        Constructor.

        :param api: OpenCTI API client
        """

        self._api = api
        self._default_properties = """
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
            latitude
            longitude
            precision
            x_opencti_aliases
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
    def generate_id(
        name: str,
        x_opencti_location_type: str = None,
        latitude: str = None,
        longitude: str = None,
    ) -> str:
        """
        Generate a STIX compliant UUID5.

        :param name: Location name
        :param x_opencti_location_type: OpenCTI location type
        :param latitude: Location latitude
        :param longitude: Location longitude
        :return: A Stix compliant UUID5
        """

        if x_opencti_location_type == "position":
            data = {
                "name": name.lower().strip(),
                "latitude": latitude,
                "longitude": longitude,
            }
        else:
            data = {
                "name": name.lower().strip(),
                "x_opencti_location_type": x_opencti_location_type,
            }

        return _generate_uuid5("location", data)

    """
        List Location objects

        :param types: the list of types
        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Location objects
    """

    def list(self, **kwargs):
        types = kwargs.get("types", None)
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
            "info", "Listing Locations with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                        query Locations($types: [String], $filters: [LocationsFiltering], $search: String, $first: Int, $after: ID, $orderBy: LocationsOrdering, $orderMode: OrderingMode) {
                            locations(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                                edges {
                                    node {
                                        """
            + (
                custom_attributes
                if custom_attributes is not None
                else self._default_properties
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
                "types": types,
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self._api.process_multiple(result["data"]["locations"], with_pagination)

    """
        Read a Location object

        :param id: the id of the Location
        :param filters: the filters to apply if no id provided
        :return Location object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Location {" + id + "}.")
            query = (
                """
                            query Location($id: String!) {
                                location(id: $id) {
                                    """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self._default_properties
                )
                + """
                    }
                }
             """
            )
            result = self._api.query(query, {"id": id})
            return self._api.process_multiple_fields(result["data"]["location"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_location] Missing parameters: id or filters"
            )
            return None

    """
        Create a Location object

        :param name: the name of the Location
        :return Location object
    """

    def create(self, **kwargs):
        type = kwargs.get("type", None)
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
        latitude = kwargs.get("latitude", None)
        longitude = kwargs.get("longitude", None)
        precision = kwargs.get("precision", None)
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if name is not None:
            self._api.log("info", "Creating Location {" + name + "}.")
            query = """
                mutation LocationAdd($input: LocationAddInput) {
                    locationAdd(input: $input) {
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
                        "type": type,
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
                        "latitude": latitude,
                        "longitude": longitude,
                        "precision": precision,
                        "x_opencti_aliases": x_opencti_aliases,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(result["data"]["locationAdd"])
        else:
            self._api.log("error", "Missing parameters: name")

    """
        Import an Location object from a STIX2 object

        :param stixObject: the Stix-Object Location
        :return Location object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if "name" in stix_object:
            name = stix_object["name"]
        elif "city" in stix_object:
            name = stix_object["city"]
        elif "country" in stix_object:
            name = stix_object["country"]
        elif "region" in stix_object:
            name = stix_object["region"]
        else:
            self._api.log("error", "[opencti_location] Missing name")
            return
        if "x_opencti_location_type" in stix_object:
            type = stix_object["x_opencti_location_type"]
        elif self._api.get_attribute_in_extension("type", stix_object) is not None:
            type = self._api.get_attribute_in_extension("type", stix_object)
        else:
            if "city" in stix_object:
                type = "City"
            elif "country" in stix_object:
                type = "Country"
            elif "region" in stix_object:
                type = "Region"
            else:
                type = "Position"
        if stix_object is not None:

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
                type=type,
                stix_id=stix_object["id"],
                createdBy=extras.get("created_by_id"),
                objectMarking=extras.get("object_marking_ids", []),
                objectLabel=extras.get("object_label_ids", []),
                externalReferences=extras.get("external_references_ids", []),
                revoked=stix_object.get("revoked"),
                confidence=stix_object.get("confidence"),
                lang=stix_object.get("lang"),
                created=stix_object.get("created"),
                modified=stix_object.get("modified"),
                name=name,
                description=self._api.stix2.convert_markdown(stix_object["description"])
                if "description" in stix_object
                else "",
                latitude=stix_object.get("latitude"),
                longitude=stix_object.get("longitude"),
                precision=stix_object.get("precision"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                x_opencti_aliases=self._api.stix2.pick_aliases(stix_object),
                update=update,
            )
        else:
            self._api.log("error", "[opencti_location] Missing parameters: stixObject")
