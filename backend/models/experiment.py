from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from datetime import datetime

from backend.database.database import Base


class Experiment(Base):

    __tablename__ = "experiments"

    experiment_id = Column(
        String,
        primary_key=True,
        index=True
    )

    dataset_name = Column(
        String,
        nullable=False
    )

    dataset_path = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="uploaded"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    current_agent = Column(
        String,
        nullable=True
    )

    pipeline_status = Column(
        String,
        default="uploaded"
    )

    execution_time = Column(
        Float,
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    pipeline_result = Column(
        JSON,
        nullable=True
    )