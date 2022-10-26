class RunException(Exception):
    pass


#
# class InternalImportArguments(ConnectorArguments):
#     file_id: str
#     file_mime: str
#     file_fetch: str
#     entity_id: str
#
#
# class StixImportArgument(ConnectorArguments):
#     token: str
#
#
# class InternalEnrichmentArgument(ConnectorArguments):
#     entity_id: str
#
#
# class InternalExportArgument(ConnectorArguments):
#     export_scope: str
#     export_type: str
#     file_name: str
#     max_marking: str
#     entity_type: str
#     entity_id: Optional[str]
#     list_params: Optional[List[str]]
