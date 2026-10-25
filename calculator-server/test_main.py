from fastapi.testclient import TestClient
from collections import deque
from datetime import datetime, timedelta

from app import dependencies
from app.dependencies import expand_percent, get_history
from app.main import app

client = TestClient(app)

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

def test_get_empty_history():
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is True
    r = client.get("/history")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 0

def test_get_one_history():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    r = client.get("/history")
    assert r.status_code == 200
    h = r.json()
    assert len(h) == 1
    assert h[0]['expr'] == "6%"
    assert abs(h[0]['result'] - 0.06) < 1e-9

def test_get_three_history():
    r = client.delete("/history")
    assert r.status_code == 200
    for expr in ["6%", "100 - 6%", "30/4"]:
        r = client.post("/calculate", json={"expr": expr})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True

    r = client.get("/history")
    assert r.status_code == 200
    h = r.json()
    assert len(h) == 3
    for i, (expr, expected) in enumerate([("30/4", 7.5), ("100 - 6%", 94.0), ("6%", 0.06)]):
        assert h[i]['expr'] == expr
        assert abs(h[i]['result'] - expected) < 1e-9


def test_react_request_and_response_contract():
    response = client.post("/calculate", json={"expr": "7*8"})
    assert response.status_code == 200
    assert response.json() == {
        "ok": True, "expr": {"expr": "7*8"}, "result": 56, "error": ""
    }
    entry = client.get("/history").json()[0]
    assert entry["expr"] == "7*8"
    assert entry["result"] == 56
    assert datetime.fromisoformat(entry["timestamp"]).utcoffset() == timedelta(0)


def test_failed_calculation_does_not_add_history():
    client.post("/calculate", json={"expr": "1+2"})
    for expr in ["1/0", "1+"]:
        response = client.post("/calculate", json={"expr": expr})
        assert response.status_code == 200
        assert response.json()["ok"] is False
    assert len(client.get("/history").json()) == 1
    assert client.post("/calculate", json={"expr": "2+2"}).json()["result"] == 4


def test_routes_share_injected_history():
    isolated_history = deque(maxlen=2)
    app.dependency_overrides[get_history] = lambda: isolated_history
    for expr in ["1+1", "2+2", "3+3"]:
        assert client.post("/calculate", json={"expr": expr}).json()["ok"] is True
    assert len(isolated_history) == 2
    assert [row["result"] for row in client.get("/history").json()] == [6, 4]
    assert len(client.get("/history?limit=1").json()) == 1
    assert client.get("/history?limit=-1").json() == []
    assert client.delete("/history").json() == {"ok": True, "cleared": True}
    assert len(isolated_history) == 0
    assert len(get_history()) == 0


def test_calculate_uses_expansion_dependency():
    app.dependency_overrides[expand_percent] = lambda: "10+20"
    response = client.post("/calculate", json={"expr": "5%"})
    assert response.json()["result"] == 30
    assert client.get("/history").json()[0]["expr"] == "5%"


def test_expansion_failure_does_not_reach_calculation(monkeypatch):
    class BrokenPattern:
        def search(self, expression):
            raise ValueError("Expansion failed")

    monkeypatch.setattr(dependencies, "_percent_pair", BrokenPattern())
    response = client.post("/calculate", json={"expr": "5%"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Could not expand the expression."}
    assert client.get("/history").json() == []


def test_invalid_request_body():
    for body in [{}, {"expr": None}, {"expr": 123}]:
        assert client.post("/calculate", json=body).status_code == 422
