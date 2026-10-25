import math
from collections import deque

from asteval import Interpreter
from fastapi import APIRouter, Depends

from app.dependencies import expand_percent, get_history
from app.schemas import ExpressionIn, ExpressionOut

router = APIRouter(tags=["calculator"])


@router.post("/calculate")
def calculate(
    expr: ExpressionIn,
    code: str = Depends(expand_percent),
    history: deque[ExpressionOut] = Depends(get_history),
):
    try:
        # Each calculation gets its own evaluator and error state.
        aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        history.appendleft(ExpressionOut(expr=expr.expr, result=result))
        return {"ok": True, "expr": expr, "result": result, "error": ""}
    except Exception as exc:
        return {"ok": False, "expr": expr, "error": str(exc)}
