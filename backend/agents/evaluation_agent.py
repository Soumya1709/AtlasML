
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class EvaluationAgent(BaseAgent):
    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "EvaluationAgent"
        state.status = "running"

        model = state.best_model or state.trained_model
        X_test = state.X_test
        y_test = state.y_test

        if model is None:
            raise ValueError(
                "No trained model found. Run TrainingAgent and "
                "HyperparameterTuningAgent first."
            )

        if X_test is None or y_test is None:
            raise ValueError(
                "Test data is missing. Run TrainingAgent first."
            )

        if len(X_test) == 0 or len(y_test) == 0:
            raise ValueError("The test dataset is empty.")

        predictions = model.predict(X_test)

        problem_type = str(
            state.summary.get("problem_type", "")
        ).lower()

        if "classification" in problem_type:
            metrics = {
                "problem_type": "classification",
                "accuracy": float(
                    accuracy_score(y_test, predictions)
                ),
                "precision_weighted": float(
                    precision_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )
                ),
                "recall_weighted": float(
                    recall_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )
                ),
                "f1_weighted": float(
                    f1_score(
                        y_test,
                        predictions,
                        average="weighted",
                        zero_division=0,
                    )
                ),
                "confusion_matrix": confusion_matrix(
                    y_test, predictions
                ).tolist(),
            }

        elif "regression" in problem_type:
            mse = mean_squared_error(y_test, predictions)

            metrics = {
                "problem_type": "regression",
                "mae": float(
                    mean_absolute_error(y_test, predictions)
                ),
                "mse": float(mse),
                "rmse": float(mse ** 0.5),
                "r2": float(r2_score(y_test, predictions)),
            }

        else:
            raise ValueError(
                f"Unsupported problem type: {problem_type!r}. "
                "Expected classification or regression."
            )

        metrics["model_name"] = getattr(
            state, "best_model_name", None
        )
        metrics["test_rows"] = int(len(y_test))

        state.metrics = metrics
        state.summary["evaluation"] = metrics

        if "EvaluationAgent" not in state.executed_agents:
            state.executed_agents.append("EvaluationAgent")

        state.status = "completed"

        logger.info(
            "Evaluation completed for model %s",
            metrics["model_name"],
        )

        return state
