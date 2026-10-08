from datetime import datetime

from pydantic import BaseModel


class AgentSummary(BaseModel):
    agent_name: str
    status: str
    execution_time: float | None = None
    attempt_number: int


class ArtifactSummary(BaseModel):
    artifact_id: str
    artifact_name: str
    artifact_type: str
    file_path: str


class ExperimentSummary(BaseModel):
    experiment_id: str
    dataset_name: str
    status: str
    pipeline_status: str
    execution_time: float | None = None
    created_at: datetime
    updated_at: datetime
    agents: list[AgentSummary]
    artifacts: list[ArtifactSummary]