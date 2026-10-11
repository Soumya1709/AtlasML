import pandas as pd

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class CleaningAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:

        logger.info("========== CLEANING AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)

        original_rows = len(dataframe)

       
        dataframe = dataframe.drop_duplicates()

        duplicates_removed = (
            original_rows - len(dataframe)
        )

        
for column in dataframe.columns:
    if dataframe[column].isnull().sum() == 0:
        continue

    if dataframe[column].isnull().all():
        dataframe.drop(columns=[column], inplace=True)
        continue

    if pd.api.types.is_numeric_dtype(dataframe[column]):
        dataframe[column] = dataframe[column].fillna(
            dataframe[column].median()
        )
    else:
        modes = dataframe[column].mode()
        fill_value = modes.iloc[0] if not modes.empty else "Unknown"
        dataframe[column] = dataframe[column].fillna(fill_value)

        state.cleaned_dataframe = dataframe

        state.summary["cleaning"] = {
            "original_rows": original_rows,
            "final_rows": len(dataframe),
            "duplicates_removed": duplicates_removed,
            "missing_values_remaining": int(
                dataframe.isnull().sum().sum()
            ),
        }

        state.current_agent = "cleaning_agent"
        state.status = "success"

        if hasattr(state, "executed_agents"):
            state.executed_agents.append(
                "CleaningAgent"
            )

        logger.info(
            f"Duplicates removed: {duplicates_removed}"
        )

        logger.info(
            f"Rows after cleaning: {len(dataframe)}"
        )

        logger.info(
            "Cleaning Agent Completed"
        )

        return state