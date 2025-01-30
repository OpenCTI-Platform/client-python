class OpenCTIApiTrash:
    """OpenCTIApiTrash"""

    def __init__(self, api):
        self.api = api

    def delete_operation_restore(self, operation_id: str):
        query = """
            mutation DeleteOperationRestore($id: ID!) {
                deleteOperationRestore(id: $id)
            }
           """
        self.api.query(
            query,
            {
                "id": operation_id,
            },
        )
