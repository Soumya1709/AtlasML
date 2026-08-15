from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ExperimentResponse(BaseModel):
    experiment_id: str
    dataset_name: str
    dataset_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    current_agent: str | None = None
    pipeline_status: str = "uploaded"
    execution_time: float | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)