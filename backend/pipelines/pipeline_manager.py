
import time
from pathlib import Path

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.models.pipeline_state import PipelineState

from backend.agents.dataset_agent import DatasetAgent
from backend.agents.cleaning_agent import CleaningAgent
from backend.agents.eda_agent import EDAAgent
from backend.agents.feature_agent import FeatureAgent
from backend.agents.model_selection_agent import ModelSelectionAgent
from backend.agents.training_agent import TrainingAgent
from backend.agents.hyperparameter_tuning_agent import HyperparameterTuningAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.shap_agent import SHAPAgent
from backend.agents.deployment_agent import DeploymentAgent
from backend.agents.report_agent import ReportAgent

from backend.services.experiment_service import update_experiment_status

from backend.services.agent_execution_service import (
    create_agent_execution,
    complete_agent_execution,
    fail_agent_execution,
    get_next_attempt_number,
    get_experiment_agent_executions,
)

from backend.services.artifact_service import (
    save_json_artifact,
    save_metrics_artifact,
    create_file_artifact,
    get_experiment_artifacts,
)

from backend.services.mlflow_service import (
    start_mlflow_run,
    log_pipeline_info,
    log_metric,
    log_artifact,
    end_mlflow_run,
)

from backend.services.artifact_types import (
    METRICS,
    MODEL,
    REPORT,
)


MAX_AGENT_ATTEMPTS = 3


class PipelineManager:

    def __init__(self):
        self.agents = [
            DatasetAgent(),
            CleaningAgent(),
            EDAAgent(),
            FeatureAgent(),
            ModelSelectionAgent(),
            TrainingAgent(),
            HyperparameterTuningAgent(),
            EvaluationAgent(),
            SHAPAgent(),
            DeploymentAgent(),
            ReportAgent(),
        ]

    def register_artifact(
        self,
        db: Session,
        experiment_id: str,
        artifact_name: str,
        artifact_type: str,
        file_path: str,
    ):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Artifact file not found: {file_path}"
            )

        existing_artifacts = get_experiment_artifacts(
            db=db,
            experiment_id=experiment_id,
        )

        for artifact in existing_artifacts:
            if artifact.artifact_name == artifact_name:
                artifact.file_path = str(path)
                artifact.artifact_type = artifact_type

                db.commit()
                db.refresh(artifact)

                return artifact

        return create_file_artifact(
            db=db,
            experiment_id=experiment_id,
            artifact_name=artifact_name,
            artifact_type=artifact_type,
            file_path=str(path),
        )

    def run_pipeline(
        self,
        state: PipelineState,
        db: Session,
    ) -> PipelineState:

        logger.info("========== PIPELINE STARTED ==========")

        pipeline_start = time.time()
        dataset_name = Path(state.dataset_path).name

        try:
            # Start MLflow tracking
            start_mlflow_run(
                experiment_name="AtlasML",
                run_name=f"{dataset_name}_{state.experiment_id}",
            )

            log_pipeline_info(
                experiment_id=state.experiment_id,
                dataset_name=dataset_name,
                rows=int(state.summary.get("rows") or 0),
                columns=int(state.summary.get("columns") or 0),
            )

            # Execute all agents in sequence with retries
            for agent in self.agents:

                agent_name = agent.__class__.__name__

                logger.info("Running %s", agent_name)

                state.current_agent = agent_name

                agent_succeeded = False

                for attempt_index in range(
                    1,
                    MAX_AGENT_ATTEMPTS + 1,
                ):
                    attempt_number = get_next_attempt_number(
                        db=db,
                        experiment_id=state.experiment_id,
                        agent_name=agent_name,
                    )

                    execution = create_agent_execution(
                        db=db,
                        experiment_id=state.experiment_id,
                        agent_name=agent_name,
                        attempt_number=attempt_number,
                    )

                    agent_start = time.time()

                    try:
                        state = agent.run(state)

                        agent_execution_time = round(
                            time.time() - agent_start,
                            2,
                        )

                        complete_agent_execution(
                            db=db,
                            execution_id=execution.execution_id,
                            execution_time=agent_execution_time,
                        )

                        log_metric(
                            f"{agent_name}_execution_time",
                            agent_execution_time,
                        )

                        logger.info(
                            "%s completed on attempt %s in %s seconds",
                            agent_name,
                            attempt_index,
                            agent_execution_time,
                        )

                        agent_succeeded = True
                        break

                    except Exception as agent_error:

                        agent_execution_time = round(
                            time.time() - agent_start,
                            2,
                        )

                        fail_agent_execution(
                            db=db,
                            execution_id=execution.execution_id,
                            error_message=str(agent_error),
                            execution_time=agent_execution_time,
                        )

                        logger.exception(
                            "%s failed on attempt %s/%s",
                            agent_name,
                            attempt_index,
                            MAX_AGENT_ATTEMPTS,
                        )

                        if attempt_index == MAX_AGENT_ATTEMPTS:
                            logger.error(
                                "%s exhausted all retry attempts",
                                agent_name,
                            )
                            raise

                        logger.warning(
                            "Retrying %s: attempt %s of %s",
                            agent_name,
                            attempt_index + 1,
                            MAX_AGENT_ATTEMPTS,
                        )

                if not agent_succeeded:
                    raise RuntimeError(
                        f"{agent_name} failed after all retry attempts."
                    )

            # Calculate total pipeline execution time
            pipeline_execution_time = round(
                time.time() - pipeline_start,
                2,
            )

            log_metric(
                "pipeline_execution_time",
                pipeline_execution_time,
            )

            # Collect agent execution metrics
            agent_executions = get_experiment_agent_executions(
                db=db,
                experiment_id=state.experiment_id,
            )

            pipeline_metrics = {
                "pipeline_execution_time": pipeline_execution_time,
            }

            for execution in agent_executions:
                if execution.execution_time is not None:
                    pipeline_metrics[
                        f"{execution.agent_name}_execution_time"
                    ] = execution.execution_time

            # Save metrics artifact
            save_metrics_artifact(
                db=db,
                experiment_id=state.experiment_id,
                metrics=pipeline_metrics,
            )

            # Save final pipeline summary
            state.summary["executed_agents"] = list(
                state.executed_agents
            )
            state.summary["pipeline_execution_time"] = (
                pipeline_execution_time
            )
            state.summary["pipeline_status"] = "completed"

            summary_artifact = save_json_artifact(
                db=db,
                experiment_id=state.experiment_id,
                artifact_name="pipeline_summary.json",
                artifact_type=METRICS,
                data=state.summary,
            )

            log_artifact(summary_artifact.file_path)
            

            # Register and log report artifact
            if state.report:
                report_path = state.report.get("report_path")
                

                if report_path and Path(report_path).exists():
                    self.register_artifact(
                        db=db,
                        experiment_id=state.experiment_id,
                        artifact_name="report.json",
                        artifact_type=REPORT,
                        file_path=report_path,
                    )

                    log_artifact(report_path)

            # Register and log deployment artifacts
            if state.deployment:
                deployment_artifacts = [
                    ("model_path", "model.pkl", MODEL),
                    ("metadata_path", "model_metadata.json", REPORT),
                ]

                for key, artifact_name, artifact_type in deployment_artifacts:
                    file_path = state.deployment.get(key)
                    

                    if file_path and Path(file_path).exists():
                        self.register_artifact(
                            db=db,
                            experiment_id=state.experiment_id,
                            artifact_name=artifact_name,
                            artifact_type=artifact_type,
                            file_path=file_path,
                        )

                        log_artifact(file_path)

            # Mark experiment as completed
            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="completed",
                current_agent="Completed",
                execution_time=pipeline_execution_time,
                pipeline_result=state.summary,
            )

            state.current_agent = "Completed"
            state.status = "completed"

            end_mlflow_run()

            logger.info(
                "========== PIPELINE COMPLETED IN %s SECONDS ==========",
                pipeline_execution_time,
            )

            return state

        except Exception as e:

            logger.exception("Pipeline Failed")

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="failed",
                current_agent=state.current_agent,
                error_message=str(e),
            )

            end_mlflow_run(status="FAILED")

            raise
