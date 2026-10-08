from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.experiment import Experiment
from backend.services.agent_execution_service import (
    get_experiment_agent_executions,
)

from backend.services.artifact_service import (
    get_experiment_artifacts,
)


def create_experiment(
    db: Session,
    dataset_name: str,
    dataset_path: str
):
    experiment = Experiment(
        experiment_id=str(uuid4()),
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        status="uploaded",
        pipeline_status="uploaded",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return experiment


def get_experiment(
    db: Session,
    experiment_id: str
):
    return (
        db.query(Experiment)
        .filter(
            Experiment.experiment_id == experiment_id
        )
        .first()
    )


def get_all_experiments(
    db: Session
):
    return db.query(Experiment).all()


def update_experiment_status(
    db: Session,
    experiment_id: str,
    status: str,
    current_agent: str | None = None,
    execution_time: float | None = None,
    error_message: str | None = None,
    pipeline_result: dict | None = None,
):
    experiment = (
        db.query(Experiment)
        .filter(
            Experiment.experiment_id == experiment_id
        )
        .first()
    )

    if experiment is None:
        return None

    experiment.status = status
    experiment.pipeline_status = status
    experiment.updated_at = datetime.utcnow()

    if current_agent is not None:
        experiment.current_agent = current_agent

    if execution_time is not None:
        experiment.execution_time = execution_time

    if error_message is not None:
        experiment.error_message = error_message

    if pipeline_result is not None:
        experiment.pipeline_result = pipeline_result

    db.commit()
    db.refresh(experiment)

    return experiment

def get_experiment_summary(
    db: Session,
    experiment_id: str,
):
    experiment = get_experiment(
        db=db,
        experiment_id=experiment_id,
    )

    if experiment is None:
        return None

    agent_executions = get_experiment_agent_executions(
        db=db,
        experiment_id=experiment_id,
    )

    artifacts = get_experiment_artifacts(
        db=db,
        experiment_id=experiment_id,
    )

    return {
        "experiment_id": experiment.experiment_id,
        "dataset_name": experiment.dataset_name,
        "status": experiment.status,
        "pipeline_status": experiment.pipeline_status,
        "execution_time": experiment.execution_time,
        "created_at": experiment.created_at,
        "updated_at": experiment.updated_at,
        "agents": agent_executions,
        "artifacts": artifacts,
    }