from backend.models.pipeline_state import PipelineState
from backend.logger import logger

from backend.services.feature_engineering import (
    extract_date_features,
    build_feature_pipeline,
    select_features,
    create_interaction_features,
    suggest_drop,
    suggest_create,
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
            []
        )

        constant_columns = summary.get(
            "constant_columns",
            []
        )

        datetime_columns = summary.get(
            "datetime_columns",
            []
        )

        high_cardinality_columns = summary.get(
            "high_cardinality_columns",
            []
        )

        target_column = summary.get(
            "target_column"
        )

        # --------------------------------------------------
        # 1. REMOVE IDENTIFIER AND CONSTANT COLUMNS
        # --------------------------------------------------

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
                inplace=True
            )

        logger.info(
            f"Removed columns: {columns_to_remove}"
        )

        # --------------------------------------------------
        # 2. DATE FEATURE EXTRACTION
        # --------------------------------------------------

        df, created_date_features = extract_date_features(
            df,
            datetime_columns
        )

        logger.info(
            f"Created date features: {created_date_features}"
        )

        # --------------------------------------------------
        # 3. BUILD FEATURE PIPELINE
        # --------------------------------------------------

        (
            feature_df,
            feature_names,
            preprocessor,
            target_values
        ) = build_feature_pipeline(
            df,
            target_column
        )

        logger.info(
            f"Generated {len(feature_names)} base features"
        )

        # --------------------------------------------------
        # 4. CREATE INTERACTION FEATURES
        # --------------------------------------------------

        numerical_features = [
            column
            for column in feature_names
            if column.startswith("numerical__")
        ]
        
        

        feature_df, interaction_features = (
            create_interaction_features(
                feature_df,
                numerical_features
            )
        )

        logger.info(
            f"Created interaction features: {interaction_features}"
        )

        # --------------------------------------------------
        # 5. FEATURE SELECTION
        # --------------------------------------------------

        feature_df, selected_features, removed_features = (
            select_features(feature_df)
        )

        logger.info(
            f"Selected {len(selected_features)} features"
        )

        logger.info(
            f"Features removed during selection: {removed_features}"
        )

        # --------------------------------------------------
        # 6. DROP SUGGESTIONS
        # --------------------------------------------------

        drop_suggestions = suggest_drop(
            df=df,
            identifier_columns=identifier_columns,
            constant_columns=constant_columns,
            high_cardinality_columns=high_cardinality_columns,
        )

        logger.info(
            f"Drop suggestions: {drop_suggestions}"
        )

        # --------------------------------------------------
        # 7. CREATE SUGGESTIONS
        # --------------------------------------------------
        
    

        create_suggestions = suggest_create(
            df=feature_df,
            numerical_columns=numerical_features,
            existing_features=interaction_features,
            max_suggestions=10,
        )

        logger.info(
            f"Create suggestions: {create_suggestions}"
        )

        # --------------------------------------------------
        # 8. SAVE STATE
        # --------------------------------------------------

        state.feature_dataframe = feature_df

        state.cleaned_dataframe = feature_df

        state.selected_features = selected_features

        state.feature_preprocessor = preprocessor

        state.target_values = target_values

        # --------------------------------------------------
        # 9. FEATURE METADATA
        # --------------------------------------------------

        state.feature_metadata = {

            "removed_columns": columns_to_remove,

            "date_features_created": created_date_features,

            "generated_feature_count": len(
                feature_df.columns
            ),

            "generated_features": (
                feature_df.columns.tolist()
            ),

            "interaction_features": interaction_features,

            "selected_feature_count": len(
                selected_features
            ),

            "selected_features": selected_features,

            "selection_removed_features": (
                removed_features
            ),

            "drop_suggestions": drop_suggestions,

            "create_suggestions": create_suggestions,

            "target_column": target_column,
        }

        # --------------------------------------------------
        # 10. COMPLETE
        # --------------------------------------------------

        state.executed_agents.append(
            "FeatureAgent"
        )

        state.status = "completed"

        logger.info(
            "Feature Agent Completed"
        )

        return state