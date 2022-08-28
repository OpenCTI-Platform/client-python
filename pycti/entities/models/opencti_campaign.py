"""OpenCTI Campaign models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "CampaignOrdering",
    "CampaignFilter",
    "CampaignFiltering",
    "ImportCampaignExtras",
]

CampaignFilter = Literal[
    "name",
    "aliases",
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


class CampaignFiltering(TypedDict):
    key: CampaignFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


CampaignOrdering = Literal[
    "name",
    "first_seen",
    "last_seen",
    "role_played",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
]


class ImportCampaignExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
