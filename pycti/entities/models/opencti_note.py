"""OpenCTI Note models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "NoteOrdering",
    "NoteFilter",
    "NoteFiltering",
    "ImportNoteExtras",
]

NoteFilter = Literal[
    "attribute_abstract",
    "content",
    "authors",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "objectContains",
    "x_opencti_workflow_id",
    "revoked",
]


class NoteFiltering(TypedDict):
    key: NoteFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


NoteOrdering = Literal[
    "attribute_abstract",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "x_opencti_workflow_id",
    "objectMarking",
]


class ImportNoteExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
