"""OpenCTI Stix Core Relationship models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixCoreRelationshipOrdering",
    "StixCoreRelationshipFilter",
    "StixCoreRelationshipFiltering",
    "ImportStixCoreRelationshipExtras",
]

StixCoreRelationshipFilter = Literal[
    "fromId",
    "toId",
    "created",
    "modified",
    "created_at",
    "confidence",
    "createdBy",
    "markedBy",
    "labelledBy",
    "toName",
    "toCreatedAt",
    "toPatternType",
    "toMainObservableType",
    "x_opencti_workflow_id",
    "revoked",
    "relationship_type",
    "fromTypes",
    "toTypes",
]


class StixCoreRelationshipFiltering(TypedDict):
    key: StixCoreRelationshipFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixCoreRelationshipOrdering = Literal[
    "entity_type",
    "relationship_type",
    "confidence",
    "start_time",
    "stop_time",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "objectMarking",
    "objectLabel",
    "killChainPhase",
    "toName",
    "toValidFrom",
    "toValidUntil",
    "toObservableValue",
    "toPatternType",
    "x_opencti_workflow_id",
    "createdBy",
]


class ImportStixCoreRelationshipExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
