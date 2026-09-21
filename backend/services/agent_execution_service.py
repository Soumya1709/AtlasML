from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.agent_execution import AgentExecution


def create_agent_execution(
    db: Session,
    experiment_id: str,
    agent_name: str,
):
    execution = AgentExecution(
        execution_id=str(uuid4()),
        experiment_id=experiment_id,
        agent_name=agent_name,
        status="running",
        started_at=datetime.utcnow(),
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    return execution


def complete_agent_execution(
    db: Session,
    execution_id: str,
    execution_time: float,
):
    execution = (
        db.query(AgentExecution)
        .filter(
            AgentExecution.execution_id == execution_id
        )
        .first()
    )

    if execution is None:
        return None

    execution.status = "completed"
    execution.completed_at = datetime.utcnow()
    execution.execution_time = execution_time

    db.commit()
    db.refresh(execution)

    return execution


def fail_agent_execution(
    db: Session,
    execution_id: str,
    error_message: str,
    execution_time: float | None = None,
):
    execution = (
        db.query(AgentExecution)
        .filter(
            AgentExecution.execution_id == execution_id
        )
        .first()
    )

    if execution is None:
        return None

    execution.status = "failed"
    execution.completed_at = datetime.utcnow()
    execution.error_message = error_message

    if execution_time is not None:
        execution.execution_time = execution_time

    db.commit()
    db.refresh(execution)

    return execution


def get_experiment_agent_executions(
    db: Session,
    experiment_id: str,
):
    return (
        db.query(AgentExecution)
        .filter(
            AgentExecution.experiment_id == experiment_id
        )
        .order_by(
            AgentExecution.started_at.asc()
        )
        .all()
    )