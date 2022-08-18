"""Attack Pattern models"""

from __future__ import annotations

from typing import List, Literal, TypedDict

from . import FilterMode

__all__ = [
    "AttackPatternOrdering",
    "AttackPatternFilter",
    "AttackPatternFiltering",
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
