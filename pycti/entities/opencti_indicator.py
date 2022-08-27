"""OpenCTI Indicator operations"""

import json
from typing import TYPE_CHECKING

from . import _generate_uuid5

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient

__all__ = [
    "Indicator",
]


class Indicator:
    """Indicator domain object"""

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
            pattern_type
            pattern_version
            pattern
            name
            description
            indicator_types
            valid_from
            valid_until
            x_opencti_score
            x_opencti_detection
            x_opencti_main_observable_type
            x_mitre_platforms
            observables {
                edges {
                    node {
                        id
                        entity_type
                        observable_value
                    }
                }
            }
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
    def generate_id(pattern: str) -> str:
        """
        Generate a STIX compliant UUID5.

        :param pattern: Indicator pattern
        :return: A Stix compliant UUID5
        """

        data = {"pattern": pattern}
        return _generate_uuid5("indicator", data)

    def list(self, **kwargs):
        """List Indicator objects

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

        :return: List of Indicators
        :rtype: list
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
            first = 100

        self._api.log(
            "info", "Listing Indicators with filters " + json.dumps(filters) + "."
        )
        query = (
            """
                                query Indicators($filters: [IndicatorsFiltering], $search: String, $first: Int, $after: ID, $orderBy: IndicatorsOrdering, $orderMode: OrderingMode) {
                                    indicators(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            data = self._api.process_multiple(result["data"]["indicators"])
            final_data = final_data + data
            while result["data"]["indicators"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["indicators"]["pageInfo"]["endCursor"]
                self._api.log("info", "Listing Indicators after " + after)
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
                data = self._api.process_multiple(result["data"]["indicators"])
                final_data = final_data + data
            return final_data
        else:
            return self._api.process_multiple(
                result["data"]["indicators"], with_pagination
            )

    def read(self, **kwargs):
        """Read an Indicator object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Indicator entity or None.

        The list method accepts the following kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided

        :return: Indicator object
        :rtype: Indicator
        """

        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self._api.log("info", "Reading Indicator {" + id + "}.")
            query = (
                """
                                    query Indicator($id: String!) {
                                        indicator(id: $id) {
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
            return self._api.process_multiple_fields(result["data"]["indicator"])
        elif filters is not None:
            result = self.list(filters=filters, customAttributes=custom_attributes)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self._api.log(
                "error", "[opencti_indicator] Missing parameters: id or filters"
            )
            return None

    def create(self, **kwargs):
        """
        Create an Indicator object

        :param str name: the name of the Indicator
        :param str pattern: stix indicator pattern
        :param str x_opencti_main_observable_type: type of the observable

        :return: Indicator object
        :rtype: Indicator
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
        pattern_type = kwargs.get("pattern_type", None)
        pattern_version = kwargs.get("pattern_version", None)
        pattern = kwargs.get("pattern", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", None)
        indicator_types = kwargs.get("indicator_types", None)
        valid_from = kwargs.get("valid_from", None)
        valid_until = kwargs.get("valid_until", None)
        x_opencti_score = kwargs.get("x_opencti_score", 50)
        x_opencti_detection = kwargs.get("x_opencti_detection", False)
        x_opencti_main_observable_type = kwargs.get(
            "x_opencti_main_observable_type", None
        )
        x_mitre_platforms = kwargs.get("x_mitre_platforms", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        create_observables = kwargs.get("x_opencti_create_observables", False)
        update = kwargs.get("update", False)

        if (
            name is not None
            and pattern is not None
            and x_opencti_main_observable_type is not None
        ):
            if x_opencti_main_observable_type == "File":
                x_opencti_main_observable_type = "StixFile"
            self._api.log("info", "Creating Indicator {" + name + "}.")
            query = """
                mutation IndicatorAdd($input: IndicatorAddInput) {
                    indicatorAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                        observables {
                            edges {
                                node {
                                    id
                                    standard_id
                                    entity_type
                                }
                            }
                        }
                    }
                }
            """
            if pattern_type is None:
                pattern_type = "stix2"
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
                        "pattern_type": pattern_type,
                        "pattern_version": pattern_version,
                        "pattern": pattern,
                        "name": name,
                        "description": description,
                        "indicator_types": indicator_types,
                        "valid_until": valid_until,
                        "valid_from": valid_from,
                        "x_opencti_score": x_opencti_score,
                        "x_opencti_detection": x_opencti_detection,
                        "x_opencti_main_observable_type": x_opencti_main_observable_type,
                        "x_mitre_platforms": x_mitre_platforms,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "killChainPhases": kill_chain_phases,
                        "createObservables": create_observables,
                        "update": update,
                    }
                },
            )
            return self._api.process_multiple_fields(result["data"]["indicatorAdd"])
        else:
            self._api.log(
                "error",
                "[opencti_indicator] Missing parameters: name or pattern or x_opencti_main_observable_type",
            )

    def add_stix_cyber_observable(self, **kwargs):
        """
        Add a Stix-Cyber-Observable object to Indicator object (based-on)

        :param id: the id of the Indicator
        :param indicator: Indicator object
        :param stix_cyber_observable_id: the id of the Stix-Observable

        :return: Boolean True if there has been no import error
        """
        id = kwargs.get("id", None)
        indicator = kwargs.get("indicator", None)
        stix_cyber_observable_id = kwargs.get("stix_cyber_observable_id", None)
        if id is not None and stix_cyber_observable_id is not None:
            if indicator is None:
                indicator = self.read(id=id)
            if indicator is None:
                self._api.log(
                    "error",
                    "[opencti_indicator] Cannot add Object Ref, indicator not found",
                )
                return False
            if stix_cyber_observable_id in indicator["observablesIds"]:
                return True
            else:
                self._api.log(
                    "info",
                    "Adding Stix-Observable {"
                    + stix_cyber_observable_id
                    + "} to Indicator {"
                    + id
                    + "}",
                )
                query = """
                    mutation StixCoreRelationshipAdd($input: StixCoreRelationshipAddInput!) {
                        stixCoreRelationshipAdd(input: $input) {
                            id
                        }
                    }
                """
                self._api.query(
                    query,
                    {
                        "id": id,
                        "input": {
                            "fromId": id,
                            "toId": stix_cyber_observable_id,
                            "relationship_type": "based-on",
                        },
                    },
                )
                return True
        else:
            self._api.log(
                "error",
                "[opencti_indicator] Missing parameters: id and stix cyber_observable_id",
            )
            return False

    def import_from_stix2(self, **kwargs):
        """
        Import an Indicator object from a STIX2 object

        :param stixObject: the Stix-Object Indicator
        :param extras: extra dict
        :param bool update: set the update flag on import

        :return: Indicator object
        :rtype: Indicator
        """
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:

            # Search in extensions
            if "x_opencti_score" not in stix_object:
                stix_object["x_opencti_score"] = self._api.get_attribute_in_extension(
                    "score", stix_object
                )
            if "x_opencti_detection" not in stix_object:
                stix_object[
                    "x_opencti_detection"
                ] = self._api.get_attribute_in_extension("detection", stix_object)
            if (
                "x_opencti_main_observable_type" not in stix_object
                and self._api.get_attribute_in_extension(
                    "main_observable_type", stix_object
                )
                is not None
            ):
                stix_object[
                    "x_opencti_main_observable_type"
                ] = self._api.get_attribute_in_extension(
                    "main_observable_type", stix_object
                )
            if "x_opencti_create_observables" not in stix_object:
                stix_object[
                    "x_opencti_create_observables"
                ] = self._api.get_attribute_in_extension(
                    "create_observables", stix_object
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
                pattern_type=stix_object.get("pattern_type"),
                pattern_version=stix_object.get("pattern_version"),
                pattern=stix_object.get("pattern", ""),
                name=stix_object.get("name", stix_object["pattern"]),
                description=self._api.stix2.convert_markdown(stix_object["description"])
                if "description" in stix_object
                else "",
                indicator_types=stix_object.get("indicator_types"),
                valid_from=stix_object.get("valid_from"),
                valid_until=stix_object.get("valid_until"),
                x_opencti_score=stix_object.get("x_opencti_score", 50),
                x_opencti_detection=stix_object.get("x_opencti_detection", False),
                x_mitre_platforms=stix_object.get("x_mitre_platforms"),
                x_opencti_main_observable_type=stix_object[
                    "x_opencti_main_observable_type"
                ]
                if "x_opencti_main_observable_type" in stix_object
                else "Unknown",
                killChainPhases=extras.get("kill_chain_phases_ids"),
                x_opencti_stix_ids=stix_object.get("x_opencti_stix_ids"),
                x_opencti_create_observables=stix_object.get(
                    "x_opencti_create_observables", False
                ),
                update=update,
            )
        else:
            self._api.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )
