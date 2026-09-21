from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.services.experiment_service import (
    get_all_experiments,
    get_experiment,
)
from backend.services.agent_execution_service import (
    get_experiment_agent_executions,
)
from backend.schemas.experiment import ExperimentResponse


router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)


@router.get(
    "",
    response_model=list[ExperimentResponse],
)
def list_experiments(
    db: Session = Depends(get_db),
):
    experiments = get_all_experiments(db)

    return experiments


@router.get(
    "/{experiment_id}/status",
)
def get_experiment_status(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    experiment = get_experiment(
        db=db,
        experiment_id=experiment_id,
    )

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found",
        )

    return {
        "experiment_id": experiment.experiment_id,
        "status": experiment.status,
        "current_agent": experiment.current_agent,
        "execution_time": experiment.execution_time,
        "error_message": experiment.error_message,
        "pipeline_result": experiment.pipeline_result,
    }
    
@router.get(
    "/{experiment_id}/agents",
)
def get_agent_executions(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    experiment = get_experiment(
        db=db,
        experiment_id=experiment_id,
    )

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found",
        )

    executions = get_experiment_agent_executions(
        db=db,
        experiment_id=experiment_id,
    )

    return executions


@router.get(
    "/{experiment_id}",
    response_model=ExperimentResponse,
)
def get_experiment_by_id(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    experiment = get_experiment(
        db=db,
        experiment_id=experiment_id,
    )

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found",
        )

    return experiment