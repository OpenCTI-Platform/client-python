from pydantic import BaseModel


class ConnectorInternal(BaseModel):
    work_id: str
    applicant_id: str


class FileEvent(BaseModel):
    file_id: str
    file_mime: str
    file_fetch: str
    entity_id: str
    bypass_validation: bool


class EnrichmentEvent(BaseModel):
    entity_id: str


class InternalFileInputMessage(BaseModel):
    internal: ConnectorInternal
    event: FileEvent


class InternalEnrichmentMessage(BaseModel):
    internal: ConnectorInternal
    event: EnrichmentEvent


class WorkerMessage(BaseModel):
    work_id: str
    applicant_id: str = None
    action_sequence: int
    entities_types: list[str]
    content: str
    update: bool = False
