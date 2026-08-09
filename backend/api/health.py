from fastapi import APIRouter
from sqlalchemy import text

from backend.database.database import engine


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health_check():

    database_status = "connected"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except Exception:
        database_status = "disconnected"

    return {
        "status": "running",
        "database": database_status,
        "service": "AtlasML Backend",
        "version": "1.0.0"
    }