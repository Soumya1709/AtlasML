from backend.models.pipeline_state import PipelineState
from backend.pipelines.pipeline_manager import PipelineManager


def execute_pipeline(state: PipelineState):

    manager = PipelineManager()

    return manager.run_pipeline(state)