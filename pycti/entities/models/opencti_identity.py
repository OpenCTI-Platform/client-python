"""OpenCTI Identity models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "IdentityOrdering",
    "IdentityFilter",
    "IdentityFiltering",
    "ImportIdentityExtras",
]

IdentityFilter = Literal[
    "entity_type",
    "identity_class",
    "name",
    "x_opencti_aliases",
    "confidence",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "x_opencti_workflow_id",
    "revoked",
]


class IdentityFiltering(TypedDict):
    key: IdentityFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


IdentityOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportIdentityExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
