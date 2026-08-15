from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import Experiment


def create_experiment(
    db: Session,
    dataset_name: str,
    dataset_path: str,
):

    experiment = Experiment(
        experiment_id=str(uuid4()),
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        status="uploaded",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(experiment)

    db.commit()

    db.refresh(experiment)

    return experiment


def get_all_experiments(db: Session):
    return (
        db.query(Experiment)
        .order_by(Experiment.created_at.desc())
        .all()
    )


def get_experiment(
    db: Session,
    experiment_id: str,
):
    return (
        db.query(Experiment)
        .filter(
            Experiment.experiment_id == experiment_id
        )
        .first()
    )

def update_experiment_status(
    db: Session,
    experiment_id: str,
    status: str,
    current_agent: str = None,
    execution_time: float = None,
    error_message: str = None,
):
    experiment = (
        db.query(Experiment)
        .filter(Experiment.experiment_id == experiment_id)
        .first()
    )

    if experiment is None:
        return None

    experiment.status = status

    if current_agent is not None:
        experiment.current_agent = current_agent

    if execution_time is not None:
        experiment.execution_time = execution_time

    if error_message is not None:
        experiment.error_message = error_message

    db.commit()
    db.refresh(experiment)

    return experiment