"""OpenCTI Stix Cyber Observable models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixCyberObservableOrdering",
    "StixCyberObservableFilter",
    "StixCyberObservableFiltering",
    "ImportStixCyberObservableExtras",
]

StixCyberObservableFilter = Literal[
    "entity_type",
    "x_opencti_score",
    "x_opencti_organization_type",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "relatedTo",
    "objectContained",
    "containedBy",
    "hasExternalReference",
    "sightedBy",
    "value",
    "name",
    "confidence",
    "hashes_MD5",
    "hashes_SHA1",
    "hashes_SHA256",
]


class StixCyberObservableFiltering(TypedDict):
    key: StixCyberObservableFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixCyberObservableOrdering = Literal[
    "entity_type",
    "created_at",
    "updated_at",
    "observable_value",
    "objectMarking",
]


class ImportStixCyberObservableExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
