"""OpenCTI Tool models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "ToolOrdering",
    "ToolFilter",
    "ToolFiltering",
    "ImportToolExtras",
]

ToolFilter = Literal[
    "name",
    "aliases",
    "created",
    "modified",
    "created_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "x_opencti_workflow_id",
]


class ToolFiltering(TypedDict):
    key: ToolFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


ToolOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportToolExtras(TypedDict, total=False):
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
