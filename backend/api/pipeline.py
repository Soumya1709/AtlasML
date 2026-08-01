from fastapi import APIRouter

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.get("/status")
def pipeline_status():

    return {
        "status": "ready",
        "message": "Pipeline Manager is ready."
    }