from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState

from backend.services.dataset_understanding import (
    detect_identifier_columns,
    detect_target_column,
    detect_problem_type,
    detect_datetime_columns,
    detect_text_columns,
    detect_constant_columns,
    detect_high_cardinality_columns,
    generate_dataset_problems,
)

import pandas as pd


class DatasetAgent(BaseAgent):

    def run(self, state: PipelineState):

        logger.info("========== DATASET AGENT ==========")

        logger.info(f"Dataset : {state.dataset_path}")
        logger.info(f"Rows : {state.summary['rows']}")
        logger.info(f"Columns : {state.summary['columns']}")

        dataframe = pd.read_csv(state.dataset_path)

        identifier_columns = detect_identifier_columns(dataframe)
        target_column = detect_target_column(dataframe)

        problem_type = detect_problem_type(
            dataframe,
            target_column
        )

        datetime_columns = detect_datetime_columns(dataframe)
        text_columns = detect_text_columns(dataframe)
        constant_columns = detect_constant_columns(dataframe)
        high_cardinality_columns = detect_high_cardinality_columns(dataframe)
        dataset_problems = generate_dataset_problems(state.summary)

        state.summary["identifier_columns"] = identifier_columns
        state.summary["target_column"] = target_column
        state.summary["problem_type"] = problem_type
        state.summary["datetime_columns"] = datetime_columns
        state.summary["text_columns"] = text_columns
        state.summary["constant_columns"] = constant_columns
        state.summary["high_cardinality_columns"] = high_cardinality_columns
        state.summary["dataset_problems"] = dataset_problems

        state.current_agent = "dataset_agent"
        state.status = "success"

        # If your PipelineState has executed_agents
        if hasattr(state, "executed_agents"):
            state.executed_agents.append("DatasetAgent")

        logger.info(f"Target Column: {target_column}")
        logger.info(f"Identifier Columns: {identifier_columns}")
        logger.info(f"Problem Type: {problem_type}")
        logger.info(f"Datetime Columns: {datetime_columns}")
        logger.info(f"Text Columns: {text_columns}")
        logger.info(f"Constant Columns: {constant_columns}")
        logger.info(f"High Cardinality Columns: {high_cardinality_columns}")
        logger.info(f"Dataset Problems: {dataset_problems}")

        logger.info("Dataset Agent Completed")

        return state