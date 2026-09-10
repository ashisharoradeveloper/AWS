from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_summary() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("products.csv", b"name,price\nWidget,10\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["total_records"] == 1


def test_analyze_endpoint_rejects_non_csv_files() -> None:
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("products.txt", b"name\nWidget\n", "text/plain")},
    )

    assert response.status_code == 400
