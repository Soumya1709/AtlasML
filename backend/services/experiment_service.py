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


def get_all_experiments(
    db: Session,
):

    return db.query(Experiment).all()