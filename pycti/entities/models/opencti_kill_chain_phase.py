"""OpenCTI Kill-Chain-Phase models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "KillChainPhaseOrdering",
    "KillChainPhaseFilter",
    "KillChainPhaseFiltering",
    "ImportKillChainPhaseExtras",
]

KillChainPhaseFilter = Literal[
    "kill_chain_name",
    "phase_name",
]


class KillChainPhaseFiltering(TypedDict):
    key: KillChainPhaseFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


KillChainPhaseOrdering = Literal[
    "x_opencti_order",
    "kill_chain_name",
    "phase_name",
    "created",
    "modified",
    "created_at",
    "updated_at",
]


class ImportKillChainPhaseExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
