from collections import deque

from fastapi import APIRouter, Depends

from app.dependencies import HISTORY_MAX, get_history
from app.schemas import ExpressionOut

router = APIRouter(tags=["history"])


@router.get("/history")
def read_history(
    limit: int = 50,
    history: deque[ExpressionOut] = Depends(get_history),
) -> list[ExpressionOut]:
    return list(history)[:max(0, min(limit, HISTORY_MAX))]


@router.delete("/history")
def clear_history(history: deque[ExpressionOut] = Depends(get_history)):
    history.clear()
    return {"ok": True, "cleared": True}
