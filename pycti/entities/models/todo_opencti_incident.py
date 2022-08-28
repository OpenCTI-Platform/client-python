"""OpenCTI Incident models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "IncidentOrdering",
    "IncidentFilter",
    "IncidentFiltering",
    "ImportIncidentExtras",
]

IncidentFilter = Literal[
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


class IncidentFiltering(TypedDict):
    key: IncidentFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


IncidentOrdering = Literal[
    "name",
    "first_seen",
    "last_seen",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
    "objectMarking",
]


class ImportIncidentExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
