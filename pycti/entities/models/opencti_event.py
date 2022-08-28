"""OpenCTI Event models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "EventOrdering",
    "EventFilter",
    "EventFiltering",
    "ImportEventExtras",
]

EventFilter = Literal[
    "name",
    "aliases",
    "event_types",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "x_opencti_workflow_id",
]


class EventFiltering(TypedDict):
    key: EventFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


EventOrdering = Literal[
    "name",
    "event_types",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "objectMarking",
    "objectLabel",
    "x_opencti_workflow_id",
]


class ImportEventExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
