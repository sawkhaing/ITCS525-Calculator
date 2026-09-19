# Mini Calculator Server

A FastAPI-based REST API for evaluating mathematical expressions with percentage logic support and safe evaluation via `asteval`.

---

## 🚀 Prerequisites

* **Python**: 3.13+
* **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`

---

## 🛠️ How to Run Manually

### Option 1: Using `uv` (Recommended)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start the FastAPI dev server**:
   ```bash
   uv run uvicorn main:app --reload
   ```
   *Alternatively, using FastAPI CLI:*
   ```bash
   uv run fastapi dev main.py
   ```

---

### Option 2: Using Standard `pip` and Virtual Environment

1. **Create and activate a virtual environment**:
   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```bash
   pip install -U pip
   pip install fastapi "uvicorn[standard]" asteval pytest httpx
   ```

3. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

---

## 📡 API Endpoints & Documentation

Once the server is running, access the interactive API docs at:
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Data Models (`models.py`)

* **`Expression`**: Request body for calculation containing `expr: str` and `expand_percent()` method.
* **`CalculatorLog`**: Calculation history entry containing `timestamp`, `expr`, and `result`.

### Endpoints Specification

#### 1. Calculate Expression
* **`POST /calculate`**
  * **Request Body** (`Expression`):
    ```json
    {
      "expr": "5 + 10%"
    }
    ```
  * **Example Request**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/calculate" \
         -H "Content-Type: application/json" \
         -d '{"expr": "5 + 10%"}'
    ```
  * **Example Response**:
    ```json
    {
      "ok": true,
      "expr": "5 + 10%",
      "result": 5.5,
      "error": ""
    }
    ```

#### 2. Get Calculation History
* **`GET /history`**
  * **Query Parameter**: `limit` (optional integer, default `50`)
  * **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/history?limit=10"
    ```
  * **Example Response** (`list[CalculatorLog]`):
    ```json
    [
      {
        "timestamp": "2026-08-27T23:20:00.000000",
        "expr": "5 + 10%",
        "result": 5.5
      }
    ]
    ```

#### 3. Clear History
* **`DELETE /history`**
  * **Example Request**:
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/history"
    ```
  * **Example Response**:
    ```json
    {
      "ok": true,
      "message": "History cleared"
    }
    ```

---

## 🧪 Running Unit Tests

Run the test suite using `pytest`:

```bash
# With uv
uv run pytest

# With activated virtual environment
pytest
```

