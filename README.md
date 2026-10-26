# ITCS525: Composing Docker Containers for Web Apps

[Lab Assignment Requirements](https://northanapon.notion.site/Composing-Docker-containers-for-Web-apps-236dd5f44b7f800ba116c1438518bd00)

This repository contains the multi-container Docker Compose architecture for the ITCS525 Calculator Web Application, composing a FastAPI backend server, a MySQL 8.4 database service with healthchecks and volume persistence, and a React + Tailwind CSS client.

---

## Architecture Overview

```text
ITCS525-Calculator/
├── calculator-server/               # Backend API + Docker Compose setup
│   ├── app/                         # FastAPI application source
│   │   ├── main.py                  # App entry point, CORS, and /test-db endpoint
│   │   ├── dependencies.py          # History injection and percentage evaluation
│   │   ├── schemas.py               # Pydantic models (ExpressionIn, ExpressionOut)
│   │   └── routers/                 # Route handlers (calculator, history)
│   ├── compose.yaml                 # Docker Compose multi-container configuration
│   ├── Dockerfile                   # Container build instructions (Python 3.13-slim)
│   ├── .dockerignore                # Build exclusions
│   ├── requirements.txt             # Locked dependencies for container build
│   ├── pyproject.toml / uv.lock     # Project dependency manifests managed with uv
│   ├── prompts.txt                  # Recorded AI prompts for configuration generation
│   └── test_*.py                    # Pytest test suite (21 unit tests)
├── calculator-react/                # React 19 + Tailwind CSS 4 frontend
│   ├── src/                         # React components (App, Button, ThemeContext)
│   └── package.json                 # Client dependencies
└── preview-dark.png                 # UI preview screenshot
```

---

## Container Architecture Specifications

| Service | Image / Build | Ports | Volumes / Mounts | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **`backend`** | Built from `./calculator-server/Dockerfile` | `34242:5000` | `./app:/app/app` (bind mount) | Runs FastAPI dev server on `0.0.0.0:5000`. Depends on `database` with `service_healthy`. |
| **`database`** | `mysql:8.4` | `127.0.0.1:54242:3306` | `dbdata:/var/lib/mysql` (named volume) | Database: `appdb`, User: `appuser`, Password: `classroom-app`. Configured with health check. |

---

## Quick Start with Docker Compose

Ensure Docker Desktop is running, then navigate to `calculator-server`:

```bash
cd calculator-server
```

### 1. Validate Compose Configuration
```bash
docker compose config
```

### 2. Build and Start Containers
```bash
docker compose up --build -d
```

### 3. Check Container Status and Health
```bash
docker compose ps
```
Both `backend` and `database` should be running, with `database` showing `(healthy)`:
```text
NAME                           SERVICE    STATUS                    PORTS
calculator-server-backend-1    backend    Up                        0.0.0.0:34242->5000/tcp
calculator-server-database-1   database   Up (healthy)              127.0.0.1:54242->3306/tcp
```

### 4. Inspect Logs
```bash
docker compose logs backend database
```

---

## Verification & Testing

### 1. HTTP & Database Connectivity (`GET /test-db`)
Verify that the FastAPI backend connects to MySQL and executes `SELECT 1`:
```bash
curl http://localhost:34242/test-db
```
**Expected response:**
```json
{"db_result":1}
```

### 2. Calculator Functionality (`POST /calculate`)
Verify that existing calculator operations are fully operational:
```bash
curl -X POST http://localhost:34242/calculate \
  -H "Content-Type: application/json" \
  -d '{"expr": "7*8"}'
```
**Expected response:**
```json
{"ok":true,"expr":{"expr":"7*8"},"result":56,"error":""}
```

Interactive API documentation is available at [http://localhost:34242/docs](http://localhost:34242/docs).

### 3. Database Data Persistence Across Container Recreation
Verify that data stored in MySQL survives container destruction and recreation:

1. **Log in to MySQL and insert test data:**
   ```bash
   docker compose exec database mysql -u appuser -pclassroom-app appdb -e "
     CREATE TABLE IF NOT EXISTS lab_check (id INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(255));
     INSERT INTO lab_check (message) VALUES ('data survives recreation');
     SELECT * FROM lab_check;
   "
   ```

2. **Destroy and recreate containers (without `-v`):**
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Verify persisted data:**
   ```bash
   docker compose exec database mysql -u appuser -pclassroom-app appdb -e "SELECT * FROM lab_check;"
   ```
   **Output:**
   ```text
   +----+--------------------------+
   | id | message                  |
   +----+--------------------------+
   |  1 | data survives recreation |
   +----+--------------------------+
   ```

#### Why this check is stronger than restarting the same container:
> **Explanation:** Simply restarting a container (e.g. `docker restart`) preserves the container instance and its internal writable layer intact, meaning data could survive in the container's temporary filesystem even without a volume configured. In contrast, `docker compose down` completely destroys the container instance and its writable layer. When `docker compose up -d` creates a brand-new container, the data surviving proves that storage truly persists in the external named volume (`dbdata:/var/lib/mysql`), decoupled from the container's lifecycle.

### 4. Running Unit Tests
Run the test suite locally using `uv`:
```bash
cd calculator-server
uv run pytest
```
**Expected result:** `21 passed`

---

## Running the React Frontend

In a separate terminal:
```bash
cd calculator-react
npm ci
npm run dev
```
Open `http://localhost:5173` in your browser to use the calculator interface.

---

## Stopping Containers
To stop and remove running containers:
```bash
cd calculator-server
docker compose down
```
*(To also remove the persistent database volume, use `docker compose down -v`)*
