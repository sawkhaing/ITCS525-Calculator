import math
from collections import deque
from fastapi import APIRouter, Depends
from asteval import Interpreter

from app.schemas import Expression, CalculatorLog
from app.dependencies import expand_percent, get_history

router = APIRouter()
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

@router.post("/calculate")
def calculate(
    expression: Expression,
    code: str = Depends(expand_percent),
    history_queue: deque = Depends(get_history)
):
    try:
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expression.expr, "result": "", "error": msg}

        log_entry = CalculatorLog(expr=expression.expr, result=result)
        history_queue.append(log_entry)
        return {"ok": True, "expr": expression.expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expression.expr, "error": str(e)}
