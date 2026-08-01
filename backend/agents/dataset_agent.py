from backend.models.pipeline_state import PipelineState
from backend.logger import logger


class DatasetAgent:

    def run(self, state: PipelineState):

        logger.info("Dataset Agent Started")

        logger.info(f"Dataset Path: {state.dataset_path}")

        logger.info(f"Rows: {state.summary['rows']}")

        state.current_agent = "dataset_agent"

        state.status = "completed"

        logger.info("Dataset Agent Finished")

        return state