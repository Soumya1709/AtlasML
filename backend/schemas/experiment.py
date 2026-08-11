from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ExperimentResponse(BaseModel):

    experiment_id: str

    dataset_name: str

    dataset_path: str

    status: str

    current_agent: Optional[str] = None

    execution_time: Optional[float] = None

    error_message: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True