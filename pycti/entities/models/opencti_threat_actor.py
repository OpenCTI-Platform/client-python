"""OpenCTI Threat-Actor models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "ThreatActorOrdering",
    "ThreatActorFilter",
    "ThreatActorFiltering",
    "ImportThreatActorExtras",
]

ThreatActorFilter = Literal[
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


class ThreatActorFiltering(TypedDict):
    key: ThreatActorFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


ThreatActorOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportThreatActorExtras(TypedDict, total=False):
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
