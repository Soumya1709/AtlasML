
import json
from pathlib import Path
from datetime import datetime, timezone

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class ReportAgent(BaseAgent):
    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "ReportAgent"
        state.status = "running"

        output_dir = Path("artifacts") / state.experiment_id / "report"
        output_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "experiment_id": state.experiment_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset": {
                "path": state.dataset_path,
                "rows": state.summary.get("rows"),
                "columns": state.summary.get("columns"),
                "target_column": state.summary.get("target_column"),
                "problem_type": state.summary.get("problem_type"),
            },
            "executed_agents": list(state.executed_agents),
            "selected_features": state.selected_features or [],
            "selected_model": getattr(state, "best_model_name", None),
            "evaluation_metrics": state.metrics or {},
            "hyperparameter_tuning": getattr(
                state, "tuning_results", None
            ) or state.summary.get("hyperparameter_tuning", {}),
            "explainability": state.shap_values or {},
            "deployment": getattr(state, "deployment", None) or {},
        }

        report_path = output_dir / "report.json"
        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, default=str)

        state.report = {
            **report,
            "report_path": str(report_path.resolve()),
        }
        state.summary["report"] = state.report

        if "ReportAgent" not in state.executed_agents:
            state.executed_agents.append("ReportAgent")

        state.status = "completed"
        logger.info("Pipeline report saved to %s", report_path)

        return state
