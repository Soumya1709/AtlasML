
import numpy as np

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class SHAPAgent(BaseAgent):
    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "SHAPAgent"
        state.status = "running"

        model = state.best_model or state.trained_model
        X_test = state.X_test
        X_train = state.X_train
        feature_names = (
            list(X_test.columns)
            if X_test is not None and hasattr(X_test, "columns")
            else state.selected_features or []
        )

        if model is None:
            raise ValueError(
                "SHAPAgent requires a trained model."
            )

        explanation = {
            "method": None,
            "feature_importance": [],
            "note": None,
        }

        # Prefer native importance when the estimator supports it.
        estimator = model
        if hasattr(model, "named_steps"):
            estimator = model.named_steps.get("model", model)

        native_importance = getattr(
            estimator, "feature_importances_", None
        )

        if native_importance is not None:
            importance = np.asarray(native_importance).ravel()
            names = feature_names

            if len(names) != len(importance):
                names = [
                    f"feature_{index}"
                    for index in range(len(importance))
                ]

            explanation["method"] = "model_feature_importance"
            explanation["feature_importance"] = [
                {
                    "feature": str(name),
                    "importance": float(value),
                }
                for name, value in sorted(
                    zip(names, importance),
                    key=lambda item: abs(item[1]),
                    reverse=True,
                )
            ]
            explanation["note"] = (
                "Native model feature importance was used; "
                "these are not SHAP values."
            )

        else:
            coefficients = getattr(estimator, "coef_", None)

            if coefficients is not None:
                importance = np.abs(
                    np.asarray(coefficients)
                )
                if importance.ndim > 1:
                    importance = importance.mean(axis=0)

                names = feature_names
                if len(names) != len(importance):
                    names = [
                        f"feature_{index}"
                        for index in range(len(importance))
                    ]

                explanation["method"] = "absolute_model_coefficients"
                explanation["feature_importance"] = [
                    {
                        "feature": str(name),
                        "importance": float(value),
                    }
                    for name, value in sorted(
                        zip(names, importance),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ]
                explanation["note"] = (
                    "Absolute model coefficients were used as a "
                    "simple importance estimate; these are not SHAP values."
                )

            elif X_train is not None and X_test is not None:
                try:
                    import shap

                    # Limit sample size to keep explanations practical.
                    background = X_train.sample(
                        n=min(50, len(X_train)),
                        random_state=42,
                    )
                    samples = X_test.sample(
                        n=min(20, len(X_test)),
                        random_state=42,
                    )

                    explainer = shap.Explainer(
                        model.predict,
                        background,
                    )
                    shap_result = explainer(samples)
                    values = np.asarray(shap_result.values)

                    if values.ndim == 3:
                        values = np.abs(values).mean(axis=(0, 2))
                    elif values.ndim == 2:
                        values = np.abs(values).mean(axis=0)
                    else:
                        values = np.abs(values).reshape(-1)

                    names = list(samples.columns)
                    if len(names) != len(values):
                        names = [
                            f"feature_{index}"
                            for index in range(len(values))
                        ]

                    explanation["method"] = "shap"
                    explanation["feature_importance"] = [
                        {
                            "feature": str(name),
                            "importance": float(value),
                        }
                        for name, value in sorted(
                            zip(names, values),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ]
                    explanation["note"] = (
                        "Mean absolute SHAP values over a limited test sample."
                    )

                except Exception as exc:
                    logger.warning(
                        "SHAP explanation could not be computed: %s",
                        exc,
                    )
                    explanation["method"] = "unavailable"
                    explanation["note"] = (
                        "SHAP explanation failed, and the selected model "
                        "does not expose native feature importance or coefficients."
                    )
                    explanation["error"] = str(exc)
            else:
                explanation["method"] = "unavailable"
                explanation["note"] = (
                    "No compatible feature importance method or data was available."
                )

        state.shap_values = explanation
        state.summary["explainability"] = explanation

        if "SHAPAgent" not in state.executed_agents:
            state.executed_agents.append("SHAPAgent")

        state.status = "completed"
        logger.info(
            "Explainability completed using method: %s",
            explanation["method"],
        )
        return state
