"""OpenCTI Stix Core Object models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixCoreObjectOrdering",
    "StixCoreObjectFilter",
    "StixCoreObjectFiltering",
    "ImportStixCoreObjectExtras",
]

StixCoreObjectFilter = Literal[
    "id",
    "standard_id",
    "name",
    "created",
    "modified",
    "created_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "hasExternalReference",
    "objectContains",
    "containedBy",
    "indicates",
    "confidence",
]


class StixCoreObjectFiltering(TypedDict):
    key: StixCoreObjectFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixCoreObjectOrdering = Literal[
    "name",
    "entity_type",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "published",
    "valid_from",
    "valid_to",
    "indicator_pattern",
]


class ImportStixCoreObjectExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
