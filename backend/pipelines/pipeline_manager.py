import time

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.models.pipeline_state import PipelineState
from backend.agents.dataset_agent import DatasetAgent
from backend.services.experiment_service import update_experiment_status


class PipelineManager:

    def __init__(self):

        self.agents = [
            DatasetAgent(),
        ]

    def run_pipeline(
        self,
        state: PipelineState,
        db: Session,
    ) -> PipelineState:

        logger.info("========== PIPELINE STARTED ==========")

        start = time.time()

        try:
            
            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="running",
                current_agent="DatasetAgent",
            )

            for agent in self.agents:

                logger.info(
                    f"Running {agent.__class__.__name__}"
                )

                state.current_agent = agent.__class__.__name__

                state = agent.run(state)

            end = time.time()

            execution_time = round(end - start, 2)

            logger.info(
                f"Pipeline Completed in {execution_time} seconds"
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

            logger.exception("Pipeline Failed")

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="failed",
                current_agent=state.current_agent,
                error_message=str(e),
            )

            raise