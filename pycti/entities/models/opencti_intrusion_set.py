"""OpenCTI Intrusion-Set models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "IntrusionSetOrdering",
    "IntrusionSetFilter",
    "IntrusionSetFiltering",
    "ImportIntrusionSetExtras",
]

IntrusionSetFilter = Literal[
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
    "revoked",
]


class IntrusionSetFiltering(TypedDict):
    key: IntrusionSetFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


IntrusionSetOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportIntrusionSetExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
