# coding: utf-8

import json
import uuid

from stix2.canonicalization.Canonicalize import canonicalize


class SecurityCoverage:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            standard_id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            objectCovered {
                __typename
                ... on StixCoreObject {
                  id
                }
            }
            objectMarking {
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
        """

    @staticmethod
    def generate_id(covered_ref):
        data = {"covered_ref": covered_ref.lower().strip()}
        data = canonicalize(data, utf8=False)
        id = str(uuid.uuid5(uuid.UUID("00abedb4-aa42-466c-9c01-fed23315a9b7"), data))
        return "security-coverage--" + id

    @staticmethod
    def generate_id_from_data(data):
        return SecurityCoverage.generate_id(data["covered_ref"])

    """
        List securityCoverage objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of SecurityCoverage objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
        first = kwargs.get("first", 100)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)

        self.opencti.app_logger.info(
            "Listing SecurityCoverage with filters", {"filters": json.dumps(filters)}
        )
        query = (
            """
                query SecurityCoverage($filters: FilterGroup, $search: String, $first: Int, $after: ID, $orderBy: SecurityCoverageOrdering, $orderMode: OrderingMode) {
                    securityCoverages(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                        edges {
                            node {
                                """
            + (custom_attributes if custom_attributes is not None else self.properties)
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
        result = self.opencti.query(
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
            data = self.opencti.process_multiple(result["data"]["securityCoverages"])
            final_data = final_data + data
            while result["data"]["securityCoverages"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["securityCoverages"]["pageInfo"]["endCursor"]
                self.opencti.app_logger.info(
                    "Listing SecurityCoverage", {"after": after}
                )
                result = self.opencti.query(
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
                data = self.opencti.process_multiple(
                    result["data"]["securityCoverages"]
                )
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["securityCoverages"], with_pagination
            )

    """
        Read a SecurityCoverage object

        :param id: the id of the SecurityCoverage
        :param filters: the filters to apply if no id provided
        :return SecurityCoverage object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.app_logger.info("Reading SecurityCoverage", {"id": id})
            query = (
                """
                    query SecurityCoverage($id: String!) {
                        securityCoverage(id: $id) {
                            """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """
                    }
                }
             """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(
                result["data"]["securityCoverage"]
            )
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.app_logger.error(
                "[opencti_security_coverage] Missing parameters: id or filters"
            )
            return None
