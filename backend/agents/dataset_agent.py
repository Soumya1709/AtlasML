from backend.agents.base_agent import BaseAgent
from backend.models.pipeline_state import PipelineState
from backend.logger import logger


class DatasetAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:

        logger.info("========== DATASET AGENT ==========")

        logger.info(f"Dataset : {state.dataset_path}")

        logger.info(f"Rows : {state.summary['rows']}")

        logger.info(f"Columns : {state.summary['columns']}")

        state.current_agent = "DatasetAgent"

        state.status = "completed"

        state.executed_agents.append("DatasetAgent")

        logger.info("Dataset Agent Completed")

        return state