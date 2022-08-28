"""OpenCTI Attack-Pattern models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "AttackPatternOrdering",
    "AttackPatternFilter",
    "AttackPatternFiltering",
    "ImportAttackPatternExtras",
]

AttackPatternFilter = Literal[
    "name",
    "aliases",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_mitre_id",
    "createdBy",
    "markedBy",
    "labelledBy",
    "mitigatedBy",
    "revoked",
    "x_opencti_workflow_id",
]


class AttackPatternFiltering(TypedDict):
    key: AttackPatternFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


AttackPatternOrdering = Literal[
    "x_mitre_id",
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportAttackPatternExtras(TypedDict, total=False):
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    kill_chain_phases_ids: List[str]
    object_ids: List[str]
    external_references_ids: List[str]
    reports: List[str]
