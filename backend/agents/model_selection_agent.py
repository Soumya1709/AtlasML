from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class ModelSelectionAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "ModelSelectionAgent"
        state.status = "running"

        problem_type = str(
            state.summary.get("problem_type", "Unknown")
        ).lower()

        if problem_type == "classification":
            candidates = {
                "LogisticRegression": LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                ),
                "RandomForestClassifier": RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
                "ExtraTreesClassifier": ExtraTreesClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
                "HistGradientBoostingClassifier":
                    HistGradientBoostingClassifier(random_state=42),
                "KNeighborsClassifier": KNeighborsClassifier(),
                "SVC": SVC(probability=True, random_state=42),
            }

        elif problem_type == "regression":
            candidates = {
                "Ridge": Ridge(),
                "RandomForestRegressor": RandomForestRegressor(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                ),
                "ExtraTreesRegressor": ExtraTreesRegressor(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                ),
                "HistGradientBoostingRegressor":
                    HistGradientBoostingRegressor(random_state=42),
            }

        else:
            raise ValueError(
                "ModelSelectionAgent cannot determine problem type. "
                "Expected Classification or Regression, but received "
                f"{state.summary.get('problem_type')!r}."
            )

        state.selected_models = candidates
        state.summary["model_selection"] = {
            "problem_type": problem_type,
            "candidate_models": list(candidates.keys()),
            "candidate_count": len(candidates),
        }

        state.executed_agents.append("ModelSelectionAgent")
        state.status = "completed"

        logger.info(
            "Selected candidate models: %s",
            list(candidates.keys()),
        )
        return state