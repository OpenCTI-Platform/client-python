class OpenCTIApiDraft:
    """OpenCTIApiDraft"""

    def __init__(self, api):
        self.api = api

    def delete(self, draft_id: str):
        query = """
            mutation DraftWorkspaceDelete($id: ID!) {
                draftWorkspaceDelete(id: $id)
            }
           """
        self.api.query(
            query,
            {
                "id": draft_id,
            },
        )
