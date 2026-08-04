from datetime import datetime
from pydantic import BaseModel


class Experiment(BaseModel):

    experiment_id: str

    dataset_name: str

    dataset_path: str

    status: str

    created_at: datetime

    updated_at: datetime