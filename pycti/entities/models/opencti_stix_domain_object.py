"""OpenCTI Stix Domain Object models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "StixDomainObjectOrdering",
    "StixDomainObjectFilter",
    "StixDomainObjectFiltering",
    "ImportStixDomainObjectExtras",
]

StixDomainObjectFilter = Literal[
    "name",
    "entity_type",
    "aliases",
    "x_opencti_aliases",
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
    "valid_from",
    "valid_until",
    "pattern_type",
    "x_opencti_main_observable_type",
    "report_types",
    "x_opencti_organization_type",
    "published",
    "x_opencti_workflow_id",
]


class StixDomainObjectFiltering(TypedDict):
    key: StixDomainObjectFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


StixDomainObjectOrdering = Literal[
    "name",
    "entity_type",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "published",
    "valid_from",
    "valid_until",
    "indicator_pattern",
    "x_opencti_workflow_id",
    "createdBy",
    "objectMarking",
]


class ImportStixDomainObjectExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
