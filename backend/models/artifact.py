from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime

from backend.database.database import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id = Column(String, primary_key=True, index=True)
    experiment_id = Column(String, nullable=False, index=True)

    artifact_name = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False)

    file_path = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )