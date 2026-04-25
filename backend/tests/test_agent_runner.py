from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cases_endpoint_returns_cases() -> None:
    response = client.get("/cases")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "fsm_stuck_bug" in response.json()


def test_run_case_returns_trajectory() -> None:
    response = client.post("/run-case/fsm_stuck_bug")

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == "fsm_stuck_bug"
    assert "actions" in data
    assert "evidence" in data
    assert "scores" in data
    assert "r_total" in data
    assert data["r_total"] >= 0.8


def test_missing_case_returns_404() -> None:
    response = client.post("/run-case/does_not_exist")

    assert response.status_code == 404


def test_traces_returns_list() -> None:
    response = client.get("/traces")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
