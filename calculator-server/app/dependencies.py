import re
from collections import deque

from fastapi import HTTPException

from app.schemas import ExpressionIn, ExpressionOut

HISTORY_MAX = 1000
history: deque[ExpressionOut] = deque(maxlen=HISTORY_MAX)

_percent_pair = re.compile(r"""
    (?P<a>\d+(?:\.\d+)?)
    \s*(?P<op>[+\-*/])\s*
    (?P<b>\d+(?:\.\d+)?)%
""", re.VERBOSE)
_number_percent = re.compile(r"(?P<n>\d+(?:\.\d+)?)%")


def get_history() -> deque[ExpressionOut]:
    """Provide the same in-memory history to both routers."""
    return history


def expand_percent(expr: ExpressionIn) -> str:
    """Expand percentage expressions before the calculation route runs."""
    try:
        s = expr.expr.replace("÷", "/").replace("×", "*").replace("−", "-")
        while True:
            m = _percent_pair.search(s)
            if not m:
                break
            a, op, b = m.group("a", "op", "b")
            if op in "+-":
                repl = f"{a} {op} (({b}/100)*{a})"
            elif op == "*":
                repl = f"{a} * ({b}/100)"
            else:
                repl = f"{a} / ({b}/100)"
            s = s[:m.start()] + repl + s[m.end():]

        return _number_percent.sub(lambda m: f"({m.group('n')}/100)", s)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail="Could not expand the expression."
        ) from exc
