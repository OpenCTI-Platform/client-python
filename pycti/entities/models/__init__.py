"""OpenCTI entity models"""

from typing import List, Literal, TypedDict

__all__ = [
    "FilterMode",
    "OrderingMode",
    "CreateEntityExtras",
]

FilterMode = Literal["and", "or"]
OrderingMode = Literal["asc", "desc"]


class CreateEntityExtras(TypedDict, total=False):
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    kill_chain_phases_ids: List[str]
    object_ids: List[str]
    external_references_ids: List[str]
    reports: List[str]
