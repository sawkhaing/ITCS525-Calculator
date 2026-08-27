import math

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from models import Expression, CalculatorLog

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})
history: list[CalculatorLog] = []

@app.post("/calculate")
def calculate(expression: Expression):
    try:
        code = expression.expand_percent()
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expression.expr, "result": "", "error": msg}
        log_entry = CalculatorLog(expr=expression.expr, result=result)
        history.append(log_entry)
        return {"ok": True, "expr": expression.expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expression.expr, "error": str(e)}

@app.get("/history", response_model=list[CalculatorLog])
def get_history(limit: int = 50):
    return history[-limit:]

@app.delete("/history")
def clear_history():
    history.clear()
    return {"ok": True, "message": "History cleared"}

