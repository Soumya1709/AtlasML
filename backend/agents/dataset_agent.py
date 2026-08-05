from backend.services.dataset_understanding import (
    detect_identifier_columns,
    detect_target_column,
    detect_problem_type,
    detect_datetime_columns
)
from backend.logger import logger
from backend.models.pipeline_state import PipelineState
import pandas as pd


class DatasetAgent:

    def run(self, state: PipelineState):

        logger.info("========== DATASET AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)

        identifier_columns = detect_identifier_columns(dataframe)
        target_column = detect_target_column(dataframe)

        problem_type = detect_problem_type(
    dataframe,
    target_column
)

        state.summary["identifier_columns"] = identifier_columns
        state.summary["target_column"] = target_column
        state.summary["problem_type"] = problem_type
        state.current_agent = "dataset_agent"
        state.status = "success"

        logger.info(f"Target Column: {target_column}")
        logger.info(f"Identifier Columns: {identifier_columns}")
        logger.info(f"Problem Type: {problem_type}")

        return state