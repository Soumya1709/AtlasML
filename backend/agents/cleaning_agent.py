
import pandas as pd

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class CleaningAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("========== CLEANING AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)
        original_rows = len(dataframe)

        dataframe = dataframe.drop_duplicates().copy()
        duplicates_removed = original_rows - len(dataframe)

        columns_removed = []

        for column in dataframe.columns:
            if dataframe[column].isnull().sum() == 0:
                continue

            if dataframe[column].isnull().all():
                columns_removed.append(column)
                continue

            if pd.api.types.is_numeric_dtype(dataframe[column]):
                dataframe[column] = dataframe[column].fillna(
                    dataframe[column].median()
                )
            else:
                modes = dataframe[column].mode()
                fill_value = (
                    modes.iloc[0] if not modes.empty else "Unknown"
                )
                dataframe[column] = dataframe[column].fillna(
                    fill_value
                )

        if columns_removed:
            dataframe = dataframe.drop(columns=columns_removed)

        state.cleaned_dataframe = dataframe

        state.summary["cleaning"] = {
            "original_rows": original_rows,
            "final_rows": len(dataframe),
            "duplicates_removed": duplicates_removed,
            "columns_removed": columns_removed,
            "missing_values_remaining": int(
                dataframe.isnull().sum().sum()
            ),
        }

        state.current_agent = "CleaningAgent"
        state.status = "completed"

        if "CleaningAgent" not in state.executed_agents:
            state.executed_agents.append("CleaningAgent")

        logger.info("Duplicates removed: %s", duplicates_removed)
        logger.info("Rows after cleaning: %s", len(dataframe))
        logger.info("Cleaning Agent Completed")

        return state
