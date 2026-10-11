import numpy as np

from sklearn.model_selection import GridSearchCV, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.base import clone

from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class HyperparameterTuningAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "HyperparameterTuningAgent"
        state.status = "running"

        X = state.feature_dataframe
        y = state.target_values
        candidates = state.selected_models

        if X is None or y is None:
            raise ValueError(
                "Tuning requires feature_dataframe and target_values."
            )

        if not candidates:
            raise ValueError(
                "Tuning requires selected_models from ModelSelectionAgent."
            )

        if len(X) != len(y):
            raise ValueError(
                "Feature and target row counts do not match."
            )

        problem_type = str(
            state.summary.get("problem_type", "Unknown")
        ).lower()

        if problem_type == "classification":
            cv = StratifiedKFold(
                n_splits=3,
                shuffle=True,
                random_state=42,
            )
            scoring = "f1_weighted"
        elif problem_type == "regression":
            cv = KFold(
                n_splits=3,
                shuffle=True,
                random_state=42,
            )
            scoring = "neg_root_mean_squared_error"
        else:
            raise ValueError(
                f"Unsupported problem type: {problem_type}"
            )

        results = {}
        best_score = -np.inf
        best_model = None
        best_name = None
        best_params = {}

        for name, estimator in candidates.items():
            logger.info("Tuning candidate model: %s", name)

            try:
                # Keep preprocessing inside CV to reduce leakage.
                # The feature agent currently supplies transformed features,
                # so this imputer mainly protects against remaining NaNs.
                pipeline = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("model", clone(estimator)),
                ])

                param_grid = self._parameter_grid(estimator)

                search = GridSearchCV(
                    estimator=pipeline,
                    param_grid=param_grid,
                    scoring=scoring,
                    cv=cv,
                    n_jobs=-1,
                    refit=True,
                    error_score="raise",
                )
                search.fit(X, y)

                score = float(search.best_score_)
                results[name] = {
                    "best_score": score,
                    "best_params": search.best_params_,
                    "scoring": scoring,
                    "status": "completed",
                }

                if score > best_score:
                    best_score = score
                    best_model = search.best_estimator_
                    best_name = name
                    best_params = search.best_params_

            except Exception as exc:
                logger.exception("Tuning failed for %s", name)
                results[name] = {
                    "status": "failed",
                    "error": str(exc),
                }

        if best_model is None:
            raise RuntimeError(
                "Hyperparameter tuning failed for every candidate model."
            )

        state.best_model = best_model
        state.trained_model = best_model
        state.tuning_results = {
            "scoring": scoring,
            "best_model_name": best_name,
            "best_score": best_score,
            "best_params": best_params,
            "candidate_results": results,
        }

        state.summary["hyperparameter_tuning"] = state.tuning_results
        state.executed_agents.append("HyperparameterTuningAgent")
        state.status = "completed"

        logger.info(
            "Best model after tuning: %s (CV score: %.4f)",
            best_name,
            best_score,
        )
        return state

    @staticmethod
    def _parameter_grid(estimator):
        if isinstance(estimator, LogisticRegression):
            return {
                "model__C": [0.1, 1.0, 10.0],
            }

        if isinstance(estimator, (RandomForestClassifier, RandomForestRegressor)):
            return {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            }

        if isinstance(estimator, (ExtraTreesClassifier, ExtraTreesRegressor)):
            return {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            }

        if isinstance(estimator, (HistGradientBoostingClassifier,
                                  HistGradientBoostingRegressor)):
            return {
                "model__learning_rate": [0.05, 0.1],
                "model__max_iter": [100, 200],
            }

        if isinstance(estimator, KNeighborsClassifier):
            return {
                "model__n_neighbors": [3, 5, 7],
                "model__weights": ["uniform", "distance"],
            }

        if isinstance(estimator, SVC):
            return {
                "model__C": [0.1, 1.0, 10.0],
                "model__kernel": ["linear", "rbf"],
            }

        if isinstance(estimator, Ridge):
            return {
                "model__alpha": [0.1, 1.0, 10.0],
            }

        return {}