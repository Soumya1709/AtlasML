from backend.models.pipeline_state import PipelineState
from backend.services.data_cleaning import remove_duplicate_rows
from backend.logger import logger

import pandas as pd


class CleaningAgent:

    def run(self, state: PipelineState):

        logger.info("========== CLEANING AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)

        cleaned_dataframe, removed_rows = remove_duplicate_rows(dataframe)

        state.cleaned_dataframe = cleaned_dataframe

        state.summary["duplicate_rows_removed"] = removed_rows

        state.current_agent = "cleaning_agent"

        state.status = "success"

        logger.info(f"Duplicate Rows Removed: {removed_rows}")

        return state