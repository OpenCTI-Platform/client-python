"""OpenCTI Language models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "LanguageOrdering",
    "LanguageFilter",
    "LanguageFiltering",
    "ImportLanguageExtras",
]

LanguageFilter = Literal[
    "name",
    "aliases",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "x_opencti_workflow_id",
]


class LanguageFiltering(TypedDict):
    key: LanguageFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


LanguageOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "objectMarking",
    "objectLabel",
    "x_opencti_workflow_id",
]


class ImportLanguageExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
