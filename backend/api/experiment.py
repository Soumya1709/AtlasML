from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db

from backend.services.experiment_service import (
    get_all_experiments,
    get_experiment
)

router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"]
)


@router.get("/")
def all_experiments(
    db: Session = Depends(get_db)
):
    return get_all_experiments(db)


@router.get("/{experiment_id}")
def experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):

    experiment = get_experiment(
        db,
        experiment_id
    )

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    return experiment

@router.get("/{experiment_id}/status")
def experiment_status(
    experiment_id: str,
    db: Session = Depends(get_db),
):

    experiment = get_experiment(
        db,
        experiment_id
    )

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    return {
        "experiment_id": experiment.experiment_id,
        "status": experiment.status,
        "current_agent": experiment.current_agent,
        "execution_time": experiment.execution_time,
        "error_message": experiment.error_message,
    }