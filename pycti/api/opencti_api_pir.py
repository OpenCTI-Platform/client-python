class OpenCTIApiPir:
    """OpenCTIApiPir"""

    def __init__(self, api):
        self.api = api

    def add_pir_dependency(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        query = """
            mutation PirAddDependency($id: ID!, $input: PirDependencyAddInput!) {
                pirAddDependency(id: $id, input: $input)
            }
           """
        self.api.query(
            query,
            {
                "id": id,
                "input": input,
            },
        )

    def delete_pir_dependency(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        query = """
            mutation PirDeleteDependency($id: ID!, $input: PirDeleteDependencyInput!) {
                pirDeleteDependency(id: $id, input: $input)
            }
           """
        self.api.query(
            query,
            {
                "id": id,
                "input": input,
            },
        )