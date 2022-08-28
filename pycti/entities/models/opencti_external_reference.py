"""OpenCTI External-Reference models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "ExternalReferenceOrdering",
    "ExternalReferenceFilter",
    "ExternalReferenceFiltering",
    "ImportExternalReferenceExtras",
]

ExternalReferenceFilter = Literal[
    "url",
    "usedBy",
    "source_name",
    "external_id",
]


class ExternalReferenceFiltering(TypedDict):
    key: ExternalReferenceFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


ExternalReferenceOrdering = Literal[
    "source_name",
    "url",
    "hash",
    "external_id",
    "created",
    "modified",
    "created_at",
    "updated_at",
]


class ImportExternalReferenceExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
