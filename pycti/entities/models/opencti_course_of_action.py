"""OpenCTI Course-Of-Action models"""

from typing import List

from typing_extensions import Literal, TypedDict

from .opencti_common import FilterMode

__all__ = [
    "CourseOfActionOrdering",
    "CourseOfActionFilter",
    "CourseOfActionFiltering",
    "ImportCourseOfActionExtras",
]

CourseOfActionFilter = Literal[
    "name",
    "aliases",
    "created",
    "modified",
    "created_at",
    "createdBy",
    "markedBy",
    "labelledBy",
    "mitigatedBy",
    "x_opencti_workflow_id",
    "x_mitre_id",
]


class CourseOfActionFiltering(TypedDict):
    key: CourseOfActionFilter
    values: List[str]
    operator: str
    filterMode: FilterMode


CourseOfActionOrdering = Literal[
    "name",
    "created",
    "modified",
    "created_at",
    "updated_at",
    "x_opencti_workflow_id",
    "objectMarking",
    "x_mitre_id",
]


class ImportCourseOfActionExtras(TypedDict, total=False):
    # TODO
    created_by_id: str
    object_marking_ids: List[str]
    object_label_ids: List[str]
    external_references_ids: List[str]
    kill_chain_phases_ids: List[str]
