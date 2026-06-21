from fastapi import APIRouter
from app.memory import get_history

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/history")
def history(limit: int = 50):
    return {"runs": get_history(limit)}