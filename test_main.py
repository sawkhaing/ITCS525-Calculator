from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import history

client = TestClient(app)

def setup_function():
    """Clear history before each test."""
    history.clear()

def test_basic_division():
    r = client.post("/calculate", json={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", json={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", json={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

def test_history_logging_and_retrieval():
    client.post("/calculate", json={"expr": "1 + 2"})
    client.post("/calculate", json={"expr": "3 * 4"})

    r = client.get("/history")
    assert r.status_code == 200
    logs = r.json()
    assert len(logs) == 2
    assert logs[0]["expr"] == "1 + 2"
    assert logs[0]["result"] == 3
    assert "timestamp" in logs[0]
    assert logs[1]["expr"] == "3 * 4"
    assert logs[1]["result"] == 12

def test_clear_history():
    client.post("/calculate", json={"expr": "10 + 20"})
    r_del = client.delete("/history")
    assert r_del.status_code == 200
    r_get = client.get("/history")
    assert r_get.status_code == 200
    assert r_get.json() == []