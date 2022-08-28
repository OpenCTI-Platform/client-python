"""OpenCTI Indicator models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "IndicatorOrdering",
    "IndicatorFilter",
    "IndicatorFiltering",
    "ImportIndicatorExtras",
]

IndicatorFilter = Literal[
    "name",
    "pattern_type",
    "pattern_version",
    "pattern",
    "x_opencti_main_observable_type",
    "x_opencti_score",
    "x_opencti_detection",
    "valid_from",
    "valid_until",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "basedOn",
    "indicates",
    "x_opencti_workflow_id",
    "sightedBy",
    "revoked",
]


class IndicatorFiltering(TypedDict):
    key: IndicatorFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


IndicatorOrdering = Literal[
    "pattern_type",
    "pattern_version",
    "pattern",
    "name",
    "indicator_types",
    "valid_from",
    "valid_until",
    "x_opencti_score",
    "x_opencti_detection",
    "confidence",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
    "objectMarking",
]


class ImportIndicatorExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
