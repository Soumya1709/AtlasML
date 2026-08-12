import time

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.models.pipeline_state import PipelineState

from backend.agents.agent_registry import AGENT_REGISTRY
from backend.pipelines.pipeline_config import PIPELINE_AGENTS

from backend.services.experiment_service import (
    update_experiment_status,
)


class PipelineManager:

    def __init__(self):

        self.agents = []

        for agent_name in PIPELINE_AGENTS:

            agent_class = AGENT_REGISTRY.get(agent_name)

            if agent_class is None:
                raise ValueError(
                    f"Agent '{agent_name}' is not registered."
                )

            self.agents.append(agent_class())

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
                    f"Running {agent_name}"
                )

                state.current_agent = agent_name

                update_experiment_status(
                    db=db,
                    experiment_id=state.experiment_id,
                    status="running",
                    current_agent=agent_name,
                )

                state = agent.run(state)

            execution_time = round(
                time.time() - start,
                2
            )

            state.status = "completed"
            state.current_agent = "Completed"

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="completed",
                current_agent="Completed",
                execution_time=execution_time,
            )

            logger.info(
                f"Pipeline completed in "
                f"{execution_time} seconds"
            )

            return state

        except Exception as e:

            logger.exception(
                "Pipeline execution failed"
            )

            state.status = "failed"

            update_experiment_status(
                db=db,
                experiment_id=state.experiment_id,
                status="failed",
                current_agent=state.current_agent,
                error_message=str(e),
            )

            raise