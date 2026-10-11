import json
import pickle
from pathlib import Path

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class DeploymentAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "DeploymentAgent"
        state.status = "running"

        model = state.best_model or state.trained_model

        if model is None:
            raise ValueError(
                "DeploymentAgent requires best_model or trained_model."
            )

        output_dir = Path("artifacts") / state.experiment_id / "deployment"
        output_dir.mkdir(parents=True, exist_ok=True)

        model_path = output_dir / "model.pkl"
        metadata_path = output_dir / "model_metadata.json"

        with model_path.open("wb") as file:
            pickle.dump(model, file)

        metadata = {
            "experiment_id": state.experiment_id,
            "model_path": str(model_path.resolve()),
            "problem_type": state.summary.get("problem_type"),
            "selected_features": state.selected_features or [],
            "target_column": state.summary.get("target_column"),
            "model_format": "pickle",
        }

        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2, default=str)

        state.deployment = {
            **metadata,
            "metadata_path": str(metadata_path.resolve()),
            "status": "artifact_saved",
        }

        state.summary["deployment"] = state.deployment
        state.executed_agents.append("DeploymentAgent")
        state.status = "completed"

        logger.info("Deployment artifacts saved to %s", output_dir)
        return state