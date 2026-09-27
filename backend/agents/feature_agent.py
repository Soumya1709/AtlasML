from backend.models.pipeline_state import PipelineState
from backend.logger import logger

from backend.services.feature_engineering import (
    extract_date_features,
    build_feature_pipeline,
)


class FeatureAgent:

    def run(self, state: PipelineState) -> PipelineState:

        logger.info("========== FEATURE AGENT ==========")

        state.current_agent = "FeatureAgent"
        state.status = "running"

        df = state.cleaned_dataframe

        if df is None:
            raise ValueError(
                "FeatureAgent requires cleaned_dataframe from the previous agent."
            )

        df = df.copy()

        summary = state.summary

        identifier_columns = summary.get(
            "identifier_columns",
            [],
        )

        constant_columns = summary.get(
            "constant_columns",
            [],
        )

        datetime_columns = summary.get(
            "datetime_columns",
            [],
        )

        target_column = summary.get(
            "target_column",
        )

        columns_to_remove = []

        for column in identifier_columns:
            if column in df.columns:
                columns_to_remove.append(column)

        for column in constant_columns:
            if column in df.columns:
                if column != target_column:
                    columns_to_remove.append(column)

        columns_to_remove = list(set(columns_to_remove))

        if columns_to_remove:
            df.drop(
                columns=columns_to_remove,
                inplace=True,
            )

        logger.info(
            f"Removed columns: {columns_to_remove}"
        )

        df, created_date_features = extract_date_features(
            df,
            datetime_columns,
        )

        logger.info(
            f"Created date features: {created_date_features}"
        )

        feature_df, feature_names, preprocessor = build_feature_pipeline(
            df,
            target_column,
        )

        logger.info(
            f"Generated {len(feature_names)} features"
        )

        logger.info(
            f"Generated features: {feature_names}"
        )

        state.feature_dataframe = feature_df
        state.cleaned_dataframe = feature_df

        state.selected_features = feature_names

        state.feature_preprocessor = preprocessor

        state.feature_metadata = {
            "removed_columns": columns_to_remove,
            "date_features_created": created_date_features,
            "generated_feature_count": len(feature_names),
            "generated_features": feature_names,
            "target_column": target_column,
        }

        state.executed_agents.append(
            "FeatureAgent"
        )

        state.status = "completed"

        logger.info("Feature Agent Completed")

        return state