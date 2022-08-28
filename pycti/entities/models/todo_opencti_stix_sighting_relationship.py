"""OpenCTI Stix Sighting Relationship models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixSightingRelationshipOrdering",
    "StixSightingRelationshipFilter",
    "StixSightingRelationshipFiltering",
    "ImportStixSightingRelationshipExtras",
]

StixSightingRelationshipFilter = Literal[
    "fromId",
    "toId",
    "x_opencti_negative",
    "attribute_count",
    "created",
    "modified",
    "created_at",
    "confidence",
    "createdBy",
    "markedBy",
    "labelledBy",
    "toPatternType",
    "toMainObservableType",
    "x_opencti_workflow_id",
]


class StixSightingRelationshipFiltering(TypedDict):
    key: StixSightingRelationshipFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixSightingRelationshipOrdering = Literal[
    "confidence",
    "x_opencti_negative",
    "first_seen",
    "last_seen",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "objectMarking",
    "objectLabel",
    "toName",
    "toValidFrom",
    "toValidUntil",
    "toPatternType",
    "toCreatedAt",
    "attribute_count",
    "x_opencti_workflow_id",
]


class ImportStixSightingRelationshipExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
