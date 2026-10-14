
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class HyperparameterTuningAgent(BaseAgent):
    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "HyperparameterTuningAgent"
        state.status = "running"

        X_train = state.X_train
        y_train = state.y_train
        candidates = state.selected_models

        if X_train is None or y_train is None:
            raise ValueError(
                "Training data is missing. Run TrainingAgent first."
            )

        if not candidates:
            raise ValueError(
                "No candidate models found. Run ModelSelectionAgent first."
            )

        problem_type = str(
            state.summary.get("problem_type", "")
        ).lower()

        is_classification = "classification" in problem_type

        # Avoid CV failures on small datasets.
        if is_classification:
            min_class_count = int(y_train.value_counts().min())
            cv_folds = min(3, min_class_count)

            if cv_folds < 2:
                raise ValueError(
                    "At least two training examples per class are "
                    "required for cross-validation."
                )

            cv = StratifiedKFold(
                n_splits=cv_folds,
                shuffle=True,
                random_state=42,
            )
            scoring = "f1_weighted"
        else:
            cv_folds = min(3, len(y_train))

            if cv_folds < 2:
                raise ValueError(
                    "At least two training rows are required for tuning."
                )

            cv = KFold(
                n_splits=cv_folds,
                shuffle=True,
                random_state=42,
            )
            scoring = "neg_mean_squared_error"

        # Small, generic grids. Unsupported parameters are omitted
        # for each estimator.
        parameter_options = {
            "RandomForestClassifier": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            },
            "ExtraTreesClassifier": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            },
            "RandomForestRegressor": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            },
            "ExtraTreesRegressor": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [None, 10],
            },
            "LogisticRegression": {
                "model__C": [0.1, 1.0, 10.0],
            },
            "Ridge": {
                "model__alpha": [0.1, 1.0, 10.0],
            },
            "KNeighborsClassifier": {
                "model__n_neighbors": [3, 5],
            },
            "SVC": {
                "model__C": [0.1, 1.0, 10.0],
            },
        }

        tuned_models = {}
        tuning_results = {}
        failures = {}

        for name, estimator in candidates.items():
            try:
                pipeline = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("model", clone(estimator)),
                ])

                # Match the grid to the actual estimator class.
                class_name = estimator.__class__.__name__
                param_grid = parameter_options.get(class_name, {})

                if param_grid:
                    search = GridSearchCV(
                        estimator=pipeline,
                        param_grid=param_grid,
                        scoring=scoring,
                        cv=cv,
                        n_jobs=-1,
                        refit=True,
                        error_score="raise",
                    )
                    search.fit(X_train, y_train)

                    best_pipeline = search.best_estimator_
                    best_params = search.best_params_
                    best_score = float(search.best_score_)
                else:
                    # Models without a configured grid are still trained.
                    best_pipeline = pipeline.fit(X_train, y_train)
                    best_params = {}
                    best_score = None

                tuned_models[name] = best_pipeline
                tuning_results[name] = {
                    "best_params": best_params,
                    "cv_score": best_score,
                }

                logger.info(
                    "Tuning completed for %s", name
                )

            except Exception as exc:
                failures[name] = str(exc)
                logger.exception("Tuning failed for %s", name)

        if not tuned_models:
            raise RuntimeError(
                f"All candidate models failed during tuning: {failures}"
            )

        # Select the best CV-scoring model.
        valid_scores = {
            name: result["cv_score"]
            for name, result in tuning_results.items()
            if result["cv_score"] is not None
        }

        if valid_scores:
            best_name = max(valid_scores, key=valid_scores.get)
        else:
            # If no model had a CV score, retain the first successfully
            # fitted model. Evaluation will compare its test performance.
            best_name = next(iter(tuned_models))

        state.trained_models = tuned_models
        state.best_model = tuned_models[best_name]
        state.trained_model = state.best_model
        state.best_model_name = best_name

        state.tuning_results = {
            "scoring": scoring,
            "cv_folds": cv_folds,
            "models": tuning_results,
            "failed_models": failures,
            "selected_model": best_name,
        }

        state.summary["hyperparameter_tuning"] = state.tuning_results

        if "HyperparameterTuningAgent" not in state.executed_agents:
            state.executed_agents.append("HyperparameterTuningAgent")

        state.status = "completed"
        return state
