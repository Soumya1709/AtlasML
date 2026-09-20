from sqlalchemy.orm import Session

from backend.models.pipeline_state import PipelineState
from backend.pipelines.pipeline_manager import PipelineManager
from backend.database.database import SessionLocal


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