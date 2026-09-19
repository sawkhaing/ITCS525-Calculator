from collections import deque
from fastapi import APIRouter, Depends

from app.schemas import CalculatorLog
from app.dependencies import get_history

router = APIRouter(prefix="/history", tags=["history"])

@router.get("", response_model=list[CalculatorLog])
def get_history_route(limit: int = 50, history_queue: deque = Depends(get_history)):
    return list(history_queue)[-limit:]

@router.delete("")
def clear_history_route(history_queue: deque = Depends(get_history)):
    history_queue.clear()
    return {"ok": True, "message": "History cleared"}
