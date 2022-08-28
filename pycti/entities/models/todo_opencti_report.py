"""OpenCTI Report models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "ReportOrdering",
    "ReportFilter",
    "ReportFiltering",
    "ImportReportExtras",
]

ReportFilter = Literal[
    "name",
    "published",
    "published_day",
    "created",
    "created_at",
    "report_types",
    "confidence",
    "objectLabel",
    "createdBy",
    "markedBy",
    "labelledBy",
    "objectContains",
    "x_opencti_workflow_id",
    "revoked",
]


class ReportFiltering(TypedDict):
    key: ReportFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


ReportOrdering = Literal[
    "name",
    "created",
    "modified",
    "published",
    "created_at",
    "updated_at",
    "createdBy",
    "objectMarking",
    "x_opencti_workflow_id",
]


class ImportReportExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
