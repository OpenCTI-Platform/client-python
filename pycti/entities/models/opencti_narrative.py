"""OpenCTI Narrative models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "NarrativeOrdering",
    "NarrativeFilter",
    "NarrativeFiltering",
    "ImportNarrativeExtras",
]

NarrativeFilter = Literal[
    "name",
    "aliases",
    "narrative_types",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "x_opencti_workflow_id",
]


class NarrativeFiltering(TypedDict):
    key: NarrativeFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


NarrativeOrdering = Literal[
    "name",
    "narrative_types",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "objectMarking",
    "objectLabel",
    "x_opencti_workflow_id",
]


class ImportNarrativeExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
