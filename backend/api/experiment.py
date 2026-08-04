from fastapi import APIRouter, HTTPException

from backend.services.experiment_service import (
    get_all_experiments,
    get_experiment
)

router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"]
)


@router.get("/")
def all_experiments():
    return get_all_experiments()


@router.get("/{experiment_id}")
def experiment(experiment_id: str):

    experiment = get_experiment(experiment_id)

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found"
        )

    return experiment