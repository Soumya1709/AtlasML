from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
)

from sqlalchemy.orm import Session

from backend.database.database import get_db

from backend.services.experiment_service import (
    get_all_experiments,
    get_experiment,
)

from backend.services.agent_execution_service import (
    get_agent_execution,
    get_experiment_agent_executions,
)

from backend.services.pipeline_service import (
    retry_agent_background,
)

from backend.services.csv_services import (
    read_csv,
    get_dataset_summary,
)

from backend.schemas.experiment import ExperimentResponse

from backend.models.pipeline_state import PipelineState


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


@router.post(
    "/{experiment_id}/agents/{execution_id}/retry",
)
def retry_agent(
    experiment_id: str,
    execution_id: str,
    background_tasks: BackgroundTasks,
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

    execution = get_agent_execution(
        db=db,
        execution_id=execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Agent execution not found",
        )

    if execution.experiment_id != experiment_id:
        raise HTTPException(
            status_code=400,
            detail="Agent execution does not belong to this experiment.",
        )

    if execution.status != "failed":
        raise HTTPException(
            status_code=400,
            detail="Only failed agent executions can be retried.",
        )

    try:

        dataframe = read_csv(
            experiment.dataset_path
        )

        summary = get_dataset_summary(
            dataframe
        )

        state = PipelineState(
            experiment_id=experiment.experiment_id,
            dataset_path=experiment.dataset_path,
            summary=summary,
            current_agent=execution.agent_name,
            status="queued",
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to prepare agent retry: {str(e)}",
        )

    background_tasks.add_task(
        retry_agent_background,
        state,
        execution.agent_name,
    )

    return {
        "message": "Agent retry started.",
        "experiment_id": experiment_id,
        "execution_id": execution_id,
        "agent_name": execution.agent_name,
    }


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