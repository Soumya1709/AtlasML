
from sklearn.base import clone
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class TrainingAgent(BaseAgent):
    """Splits the feature dataset and trains candidate models."""

    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "TrainingAgent"
        state.status = "running"

        X = state.feature_dataframe
        y = state.target_values
        candidates = state.selected_models

        if X is None or y is None:
            raise ValueError(
                "TrainingAgent requires feature_dataframe and target_values."
            )

        if not candidates:
            raise ValueError(
                "TrainingAgent requires selected_models from ModelSelectionAgent."
            )

        if len(X) != len(y):
            raise ValueError(
                "Feature and target row counts do not match."
            )

        if len(X) < 5:
            raise ValueError(
                "At least 5 rows are required for a train/test split."
            )

        problem_type = str(
            state.summary.get("problem_type", "Unknown")
        ).lower()

        stratify = None

        if problem_type == "classification":
            class_counts = y.value_counts(dropna=False)
            if len(class_counts) > 1 and class_counts.min() >= 2:
                stratify = y

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=stratify,
        )

        trained_models = {}
        failures = {}

        for name, estimator in candidates.items():
            try:
                # Imputation is fitted only on the training partition.
                model_pipeline = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("model", clone(estimator)),
                ])

                model_pipeline.fit(X_train, y_train)
                trained_models[name] = model_pipeline

                logger.info("Trained model: %s", name)

            except Exception as exc:
                failures[name] = str(exc)
                logger.exception("Training failed for %s", name)

        if not trained_models:
            raise RuntimeError(
                f"All candidate models failed to train: {failures}"
            )

        state.X_train = X_train
        state.X_test = X_test
        state.y_train = y_train
        state.y_test = y_test
        state.trained_models = trained_models

        state.summary["training"] = {
            "training_rows": int(len(X_train)),
            "testing_rows": int(len(X_test)),
            "trained_models": list(trained_models.keys()),
            "failed_models": failures,
        }

        if "TrainingAgent" not in state.executed_agents:
            state.executed_agents.append("TrainingAgent")

        state.status = "completed"

        logger.info(
            "TrainingAgent completed: %d model(s) trained.",
            len(trained_models),
        )

        return state
