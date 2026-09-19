import re
from collections import deque
from app.schemas import Expression

HISTORY_MAX = 50
history = deque(maxlen=HISTORY_MAX)

def get_history() -> deque:
    return history

def expand_percent(expression: Expression) -> str:
    percent_pair = re.compile(r"(?P<a>\d+(?:\.\d+)?)\s*(?P<op>[+\-*/])\s*(?P<b>\d+(?:\.\d+)?)%")
    number_percent = re.compile(r"(?P<n>\d+(?:\.\d+)?)%")

    s = expression.expr
    while True:
        m = percent_pair.search(s)
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

    return number_percent.sub(lambda m: f"({m.group('n')}/100)", s)
