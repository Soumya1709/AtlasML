from sqlalchemy.orm import Session

from backend.models.pipeline_state import PipelineState
from backend.pipelines.pipeline_manager import PipelineManager
from backend.database.database import SessionLocal

from backend.services.agent_execution_service import (
    create_agent_execution,
    complete_agent_execution,
    fail_agent_execution,
    get_next_attempt_number,
)


def execute_pipeline(
    state: PipelineState,
    db: Session,
) -> PipelineState:

    manager = PipelineManager()

    return manager.run_pipeline(
        state=state,
        db=db,
    )


def execute_pipeline_background(
    state: PipelineState,
) -> None:

    db = SessionLocal()

    try:
        manager = PipelineManager()

        manager.run_pipeline(
            state=state,
            db=db,
        )

    finally:
        db.close()


def retry_agent_background(
    state: PipelineState,
    agent_name: str,
) -> None:

    db = SessionLocal()

    try:

        manager = PipelineManager()

        agent = next(
            (
                current_agent
                for current_agent in manager.agents
                if current_agent.__class__.__name__ == agent_name
            ),
            None,
        )

        if agent is None:
            raise ValueError(
                f"Agent '{agent_name}' not found in pipeline."
            )

        attempt_number = get_next_attempt_number(
            db=db,
            experiment_id=state.experiment_id,
            agent_name=agent_name,
        )

        execution = create_agent_execution(
            db=db,
            experiment_id=state.experiment_id,
            agent_name=agent_name,
            attempt_number=attempt_number,
        )

        import time

        start_time = time.time()

        try:

            state.current_agent = agent_name
            state.status = "running"

            state = agent.run(state)

            execution_time = round(
                time.time() - start_time,
                2,
            )

            complete_agent_execution(
                db=db,
                execution_id=execution.execution_id,
                execution_time=execution_time,
            )

        except Exception as agent_error:

            execution_time = round(
                time.time() - start_time,
                2,
            )

            fail_agent_execution(
                db=db,
                execution_id=execution.execution_id,
                error_message=str(agent_error),
                execution_time=execution_time,
            )

            raise

    finally:
        db.close()