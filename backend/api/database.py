from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.database.database import get_db

router = APIRouter(
    prefix="/database",
    tags=["Database"]
)


@router.get("/health")
def database_health(
    db: Session = Depends(get_db)
):

    db.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }