# Calculator Server with Docker Compose & MySQL

FastAPI calculator server refactored for the [Composing Docker containers for Web apps](https://northanapon.notion.site/Composing-Docker-containers-for-Web-apps-236dd5f44b7f800ba116c1438518bd00) lab.

```text
calculator-server/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app with CORS, /test-db, and routers
│   ├── dependencies.py          # Percentage expansion and history deque injection
│   ├── schemas.py               # Pydantic schemas (ExpressionIn, ExpressionOut)
│   └── routers/
│       ├── __init__.py
│       ├── calculator.py        # POST /calculate
│       └── history.py           # GET /history, DELETE /history
├── Dockerfile                   # Python 3.13-slim image setup
├── compose.yaml                 # Multi-container Compose spec (FastAPI + MySQL 8.4)
├── .dockerignore                # Container build exclusions
├── requirements.txt             # Frozen dependencies exported via uv
├── prompts.txt                  # Recorded AI prompts for config generation
├── conftest.py                  # Pytest fixtures
├── test_dependencies.py         # Unit tests for percentage expansion & dependency injection
├── test_main.py                 # Endpoint integration tests
├── pyproject.toml
└── uv.lock
```

---

## Multi-Container Setup

- **`backend` service**: Runs FastAPI on `0.0.0.0:5000`, exposed on host port `34242`. Features a bind mount (`./app:/app/app`) for development auto-reloading and depends on the `database` service health check.
- **`database` service**: Runs MySQL 8.4 with database `appdb`, application user `appuser` (password `classroom-app`), port published at `127.0.0.1:54242:3306`, and persistent volume `dbdata:/var/lib/mysql`.

### Running with Docker Compose
```bash
docker compose up --build -d
```

### Checking Status and Logs
```bash
docker compose ps
docker compose logs -f
```

---

## API Endpoints

- **`GET /test-db`**: Verifies database connectivity with SQLAlchemy by executing `SELECT 1`. Returns `{"db_result": 1}`.
- **`POST /calculate`**: Calculates an arithmetic expression, e.g. `{"expr": "100-6%"}` -> `{"ok": true, "result": 94.0}`.
- **`GET /history`**: Retrieves calculation history.
- **`DELETE /history`**: Clears history.

Interactive Swagger API docs: `http://localhost:34242/docs`

---

## Running Locally (without Docker)

```bash
uv sync --frozen
uv run fastapi dev app/main.py
```

## Running Tests

```bash
uv run pytest
```
