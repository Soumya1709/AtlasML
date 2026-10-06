from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArtifactResponse(BaseModel):
    artifact_id: str
    experiment_id: str
    artifact_name: str
    artifact_type: str
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)