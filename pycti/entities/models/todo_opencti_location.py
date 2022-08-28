"""OpenCTI Location models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "LocationOrdering",
    "LocationFilter",
    "LocationFiltering",
    "ImportLocationExtras",
]

LocationFilter = Literal[
    "entity_type",
    "name",
    "x_opencti_aliases",
    "confidence",
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


class LocationFiltering(TypedDict):
    key: LocationFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


LocationOrdering = Literal[
    "name",
    "latitude",
    "longitude",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportLocationExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
