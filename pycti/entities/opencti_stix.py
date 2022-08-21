"""OpenCTI Stix entity operations"""

from ..api.opencti_api_client import OpenCTIApiClient


class Stix:
    """Stix entity objects"""

    def __init__(self, api: OpenCTIApiClient):
        """
        Constructor.

        :param api: OpenCTI API client
        """

        self._api = api

    """
        Delete a Stix element

        :param id: the Stix element id
        :return void
    """

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self._api.log("info", "Deleting Stix element {" + id + "}.")
            query = """
                 mutation StixEdit($id: ID!) {
                     stixEdit(id: $id) {
                         delete
                     }
                 }
             """
            self._api.query(query, {"id": id})
        else:
            self._api.log("error", "[opencti_stix] Missing parameters: id")
            return None
