from backend.models.pipeline_state import PipelineState
from backend.logger import logger


class DatasetAgent:

    def run(self, state: PipelineState) -> PipelineState:

        logger.info("========== DATASET AGENT ==========")

        logger.info(f"Dataset Path : {state.dataset_path}")

        logger.info(f"Rows : {state.summary['rows']}")

        logger.info(f"Columns : {state.summary['columns']}")

        state.current_agent = "dataset_agent"

        state.status = "completed"

        logger.info("Dataset Agent Completed")

        return state