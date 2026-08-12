import time

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.models.pipeline_state import PipelineState
from backend.agents.base_agent import BaseAgent
from backend.agents.dataset_agent import DatasetAgent

from backend.services.experiment_service import (
    update_experiment_status
)


class PipelineManager:

    def __init__(self):

        self.agents: list[BaseAgent] = [

            DatasetAgent(),

            # Add future agents here
            # CleaningAgent(),
            # FeatureEngineeringAgent(),
            # ModelSelectionAgent(),
            # TrainingAgent(),
            # EvaluationAgent(),
            # ExplainabilityAgent(),
            # ReportAgent(),

        ]

    def run_pipeline(
        self,
        state: PipelineState,
        db: Session,
    ) -> PipelineState:

        logger.info(
            "========== PIPELINE STARTED =========="
        )

        start = time.time()

        try:

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="running",
                current_agent="PipelineManager",
            )

            state.status = "running"

          

            for agent in self.agents:

                agent_name = agent.__class__.__name__

                logger.info(
                    f"Starting agent: {agent_name}"
                )

                state.current_agent = agent_name

               
                update_experiment_status(
                    db=db,
                    experiment_id=state.experiment_id,
                    status="running",
                    current_agent=agent_name,
                )

                
                state = agent.run(state)

                logger.info(
                    f"Completed agent: {agent_name}"
                )

         

            execution_time = round(
                time.time() - start,
                2
            )

            state.status = "completed"

            state.current_agent = "Completed"

            logger.info(
                f"Pipeline completed in "
                f"{execution_time} seconds"
            )

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="completed",
                current_agent="Completed",
                execution_time=execution_time,
            )

            return state

        except Exception as e:

            execution_time = round(
                time.time() - start,
                2
            )

            logger.exception(
                "Pipeline execution failed"
            )

            state.status = "failed"

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="failed",
                current_agent=state.current_agent,
                execution_time=execution_time,
                error_message=str(e),
            )

            raise