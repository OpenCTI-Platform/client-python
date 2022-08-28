"""OpenCTI Marking-Definition models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "MarkingDefinitionOrdering",
    "MarkingDefinitionFilter",
    "MarkingDefinitionFiltering",
    "ImportMarkingDefinitionExtras",
]

MarkingDefinitionFilter = Literal[
    "definition",
    "definition_type",
    "markedBy",
]


class MarkingDefinitionFiltering(TypedDict):
    key: MarkingDefinitionFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


MarkingDefinitionOrdering = Literal[
    "definition_type",
    "definition",
    "x_opencti_order",
    "x_opencti_color",
    "created",
    "modified",
    "created_at",
    "updated_at",
]


class ImportMarkingDefinitionExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
