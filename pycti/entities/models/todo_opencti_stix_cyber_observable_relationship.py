"""OpenCTI Stix Cyber Observable Relationship models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixCyberObservableRelationshipOrdering",
    "StixCyberObservableRelationshipFilter",
    "StixCyberObservableRelationshipFiltering",
    "ImportStixCyberObservableRelationshipExtras",
]

StixCyberObservableRelationshipFilter = Literal[
    "created_at",
]


class StixCyberObservableRelationshipFiltering(TypedDict):
    key: StixCyberObservableRelationshipFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixCyberObservableRelationshipOrdering = Literal[
    "relationship_type",
    "entity_type",
    "confidence",
    "start_time",
    "stop_time",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "toName",
    "toValidFrom",
    "toValidUntil",
    "toPatternType",
    "toCreatedAt",
]


class ImportStixCyberObservableRelationshipExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
