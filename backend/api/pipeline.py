from fastapi import APIRouter

from backend.pipelines.pipeline_manager import PipelineManager

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"]
)


@router.get("/info")
def pipeline_info():

    manager = PipelineManager()

    return {

        "registered_agents": [

            agent.__class__.__name__

            for agent in manager.agents

        ],

        "total_agents": len(manager.agents)
    }