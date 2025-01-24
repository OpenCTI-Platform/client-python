from typing import List, Dict


class Capability:
    """Represents a role capability on the OpenCTI platform

    The dictionary representation of a Capability has the following form::

        {
            "id": "UUID",
            "name": "Name of the capability, e.g. KNUPDATE",
            "description": "Create/Update knowledge"
        }.
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

    def list(self) -> List[Dict]:
        self.opencti.admin_logger.info("Listing capabilities")
        query = (
            """
            query CapabilityList {
                capabilities(first: 500) {
                    edges {
                        node {
                            """
            + self.properties
            + """
                        }
                    }
                }
            }
            """
        )
        result = self.opencti.query(query)
        return self.opencti.process_multiple(result["data"]["capabilities"])
