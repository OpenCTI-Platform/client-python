class OpenCTIApiInternalFile:
    """OpenCTIApiInternalFile"""

    def __init__(self, api):
        self.api = api

    def delete(self, **kwargs):
        fileName = kwargs.get("fileName", None)
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
