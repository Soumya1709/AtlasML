from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Text,
    Integer,
)

from backend.database.database import Base


class AgentExecution(Base):

    __tablename__ = "agent_executions"

    execution_id = Column(
        String,
        primary_key=True,
        index=True
    )

    experiment_id = Column(
        String,
        nullable=False,
        index=True
    )

    agent_name = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="queued"
    )

    attempt_number = Column(
        Integer,
        default=1,
        nullable=False
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    execution_time = Column(
        Float,
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )