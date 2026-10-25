# Calculator server — OOP lab solution

Refactored from the earlier calculator server to follow the [OOP lab](https://app.notion.com/p/northanapon/Apply-OOP-concepts-to-refactor-a-project-236dd5f44b7f80a094f9f5278bae5f24).

```text
calculator-server/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       ├── calculator.py
│       └── history.py
├── conftest.py
├── test_dependencies.py
├── test_main.py
├── pyproject.toml
└── uv.lock
```

`BaseExpression` defines the shared `expr` field. `ExpressionIn` inherits it, and `ExpressionOut` extends `ExpressionIn` with `result` and a timestamp generated for each entry in UTC. The old `Expression` and `CalculatorLog` names become `ExpressionIn` and `ExpressionOut`.

`dependencies.py` owns the bounded history deque. `get_history()` injects that shared history into all three routes. `expand_percent()` accepts the input schema, normalizes calculator symbols, and expands percentages before evaluation. If expansion fails, it raises HTTP 400, and the calculation route does not run.

`routers/calculator.py` defines `POST /calculate`, which depends on both expansion and history. `routers/history.py` defines `GET /history` and `DELETE /history`, which depend on history. `main.py` creates the app, configures CORS, and registers both routers.

## Run

From this directory, using Python 3.13 and uv:

```sh
uv sync --frozen
uv run fastapi dev app/main.py
```

The API runs at `http://localhost:8000`, with interactive documentation at `/docs`. The React client can use the same endpoints:

- `POST /calculate` with `{"expr": "100-6%"}` returns `{"ok": true, "expr": {"expr": "100-6%"}, "result": 94.0, "error": ""}`.
- `GET /history` returns newest-first entries with `expr`, `result`, and `timestamp`. An optional `limit` defaults to 50 and is clamped between 0 and 1000.
- `DELETE /history` returns `{"ok": true, "cleared": true}`.

Evaluation errors still return `ok: false` for compatibility with the client. Invalid request bodies return HTTP 422. History is in memory and resets when the server restarts.

## Tests

```sh
uv run pytest -q
```

Tests cover percentage expansion, failure handling, dependency overrides, shared history, and compatibility with the React API calls. The fixture clears history before and after each test so tests can run independently.
