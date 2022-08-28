"""OpenCTI Observed-Data models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "ObservedDataOrdering",
    "ObservedDataFilter",
    "ObservedDataFiltering",
    "ImportObservedDataExtras",
]

ObservedDataFilter = Literal[
    "first_observed",
    "last_observed",
    "number_observed",
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


class ObservedDataFiltering(TypedDict):
    key: ObservedDataFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


ObservedDataOrdering = Literal[
    "first_observed",
    "last_observed",
    "number_observed",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "x_opencti_workflow_id",
    "objectMarking",
]


class ImportObservedDataExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
