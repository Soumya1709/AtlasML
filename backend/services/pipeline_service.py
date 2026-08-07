from sqlalchemy.orm import Session

from backend.models.pipeline_state import PipelineState
from backend.pipelines.pipeline_manager import PipelineManager


def execute_pipeline(
    state: PipelineState,
    db: Session,
) -> PipelineState:

    manager = PipelineManager()

    return manager.run_pipeline(
        state=state,
        db=db,
    )