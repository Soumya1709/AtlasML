from backend.models.pipeline_state import PipelineState
from backend.agents.dataset_agent import DatasetAgent
from backend.logger import logger


class PipelineManager:

    def __init__(self):
        self.dataset_agent = DatasetAgent()

    def run_pipeline(self, state: PipelineState) -> PipelineState:

        logger.info("Pipeline Started")

        state = self.dataset_agent.run(state)

        logger.info("Pipeline Finished")

        return state