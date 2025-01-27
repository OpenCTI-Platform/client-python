from typing import List, Dict


class Capability:
    """Represents a role capability on the OpenCTI platform

    See the properties attribute to understand which properties are fetched by
    default from the graphql queries.
    """

    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            entity_type
            name
            description
            attribute_order
        """

    def list(self, **kwargs) -> List[Dict]:
        """Lists all capabilities available on the platform

        :param customAttributes: Custom attributes to retrieve from the GraphQL
            query.
        :type customAttributes: str, optional
        :return: List of capabilities
        :rtype: List[Dict]
        """
        customAttributes = kwargs.get("customAttributes")
        self.opencti.admin_logger.info("Listing capabilities")
        query = (
            """
            query CapabilityList {
                capabilities(first: 500) {
                    edges {
                        node {
                            """
            + (self.properties if customAttributes is None
               else customAttributes)
            + """
                        }
                    }
                }
            }
            """
        )
        result = self.opencti.query(query)
        return self.opencti.process_multiple(result["data"]["capabilities"])
