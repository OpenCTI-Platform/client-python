class OpenCTIApiInternalFile:
    """OpenCTIApiInternalFile"""

    def __init__(self, api):
        self.api = api

    def delete(self, **kwargs):
        item = kwargs.get("item", None)
        fileName = self.api.get_attribute_in_extension("id", item)
        if fileName is not None:
            query = """
                mutation InternalFileDelete($fileName: String) {
                    deleteImport(fileName: $fileName)
                }
               """
            self.api.query(
                query,
                {
                    "fileName": fileName,
                },
            )
        else:
            self.api.app_logger.error(
                "[stix_internal_file] Cant delete internal file, missing parameters: fileName"
            )
            return None
