from pydantic import BaseModel, UUID4, Json


class ConnectorInternal(BaseModel):
    work_id: str
    applicant_id: str


class FileEvent(BaseModel):
    file_id: str
    file_mime: str
    file_fetch: str
    entity_id: str
    bypass_validation: bool


class InternalFileInputMessage(BaseModel):
    internal: ConnectorInternal
    event: FileEvent


# b'{"internal":
#       {
#      "work_id":"opencti-work--dd201432-6c84-4c90-9d0b-91a926f9189c","applicant_id":"88ec0c6a-13ce-5e39-b486-354fe4a7084f"},
#       "event":{"file_id":"import/Report/87c96387-0bab-4698-9b0e-6d46a8ced827/test.pdf","file_mime":"application/pdf","file_fetch":"/storage/get/import/Report/87c96387-0bab-4698-9b0e-6d46a8ced827/test.pdf","entity_id":"87c96387-0bab-4698-9b0e-6d46a8ced827","bypass_validation":false}
#       }'
