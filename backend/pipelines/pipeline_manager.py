import time

from backend.logger import logger
from backend.models.pipeline_state import PipelineState
from backend.agents.dataset_agent import DatasetAgent


class PipelineManager:

    def __init__(self):

        self.agents = [

            DatasetAgent(),

        ]

    def run_pipeline(
        self,
        state: PipelineState
    ) -> PipelineState:

        logger.info("========== PIPELINE STARTED ==========")

        start = time.time()

        for agent in self.agents:

            logger.info(f"Running {agent.__class__.__name__}")

            state = agent.run(state)

        end = time.time()

        logger.info(
            f"Pipeline Completed in {end-start:.2f} seconds"
        )

        return state