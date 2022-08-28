"""OpenCTI Label models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "LabelOrdering",
    "LabelFilter",
    "LabelFiltering",
    "ImportLabelExtras",
]

LabelFilter = Literal[
    "value",
    "markedBy",
]


class LabelFiltering(TypedDict):
    key: LabelFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


LabelOrdering = Literal[
    "value",
    "color",
    "created",
    "modified",
    "created_at",
    "updated_at",
]


class ImportLabelExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
