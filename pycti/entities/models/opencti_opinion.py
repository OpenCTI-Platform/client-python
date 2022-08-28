"""OpenCTI Opinion models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "OpinionOrdering",
    "OpinionFilter",
    "OpinionFiltering",
    "ImportOpinionExtras",
]

OpinionFilter = Literal[
    "explanation",
    "authors",
    "opinion",
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


class OpinionFiltering(TypedDict):
    key: OpinionFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


OpinionOrdering = Literal[
    "opinion",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "objectMarking",
    "x_opencti_workflow_id",
]


class ImportOpinionExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
