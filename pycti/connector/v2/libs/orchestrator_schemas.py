from datetime import datetime
from typing import Optional, Dict, List, Union, Callable

from pydantic import BaseModel, UUID4, Json
from enum import Enum


class ConnectorArguments:
    pass


class ExecutionTypeEnum(str, Enum):
    scheduled = 'scheduled'
    triggered = 'triggered'


# ---- Connector ----


class ConnectorBase(BaseModel):
    uuid: str
    name: str
    type: str
    queue: str


class ConnectorCreate(ConnectorBase):
    config_schema: Union[Callable, Json, dict, None]


class Connector(ConnectorBase):
    id: str
    config_schema: Union[Json, dict, None]


# ---- Connector State ----

class State(str, Enum):
    pending = 'pending'
    running = 'running'
    finished = 'finished'


class Result(str, Enum):
    success = 'success'
    fail = 'fail'


class ConnectorState(BaseModel):
    state: State
    result: Result
    message: str


# ---- Config ----


class ConfigBase(BaseModel):
    connector_id: str
    name: str
    config: Union[Json, dict, None]


class ConfigCreate(ConfigBase):
    pass


class Config(ConfigBase):
    id: str

# ---- Instance ----


class InstanceBase(BaseModel):
    last_seen: int
    connector_id: str
    status: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }

class Instance(InstanceBase):
    id: str


# ---- Workflow ----


class WorkflowBase(BaseModel):
    name: str
    jobs: List[str]
    execution_type: ExecutionTypeEnum
    execution_args: Optional[str]
    token: str


class WorkflowCreate(WorkflowBase):
    pass


class Workflow(BaseModel):
    id: str


# ---- Run -----

class JobStatus(BaseModel):
    id: str
    status: State
    result: Optional[Result]


class RunBase(BaseModel):
    workflow_id: str
    applicant_id: Optional[str]
    work_id: Optional[str]
    parameters: Optional[Json]


class RunCreate(RunBase):
    pass


class Run(RunBase):
    id: str
    status: State
    result: Optional[Result]
    job_status: List[JobStatus]


class RunUpdate(BaseModel):
    command: str
    parameters: Dict


class Job(BaseModel):
    config_id: str
    queue: str


class RunContainer(BaseModel):
    token: str
    bundle: Optional[Json]
    jobs: List[Job]
    parameters: Optional[Json]
    applicant_id: Optional[str]
    work_id: Optional[str]
    run_id: str

