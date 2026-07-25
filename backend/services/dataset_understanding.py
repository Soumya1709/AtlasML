from backend.models.pipeline_state import PipelineState
from backend.services.dataset_understanding import (
    detect_identifier_columns
)

import pandas as pd


class DatasetAgent:

    def run(self, state: PipelineState):

        print("========== DATASET AGENT ==========")

        dataframe = pd.read_csv(state.dataset_path)

        identifier_columns = detect_identifier_columns(dataframe)

        state.summary["identifier_columns"] = identifier_columns

        state.current_agent = "dataset_agent"

        state.status = "success"

        print("Identifier Columns:", identifier_columns)

        return state