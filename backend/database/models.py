from sqlalchemy import Column, String, DateTime
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