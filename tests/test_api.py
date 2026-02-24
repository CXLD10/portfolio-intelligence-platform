from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_shape() -> None:
    r = client.get('/health')
    assert r.status_code == 200
    b = r.json()
    assert 'project1_status' in b
    assert 'project2_status' in b


def test_metrics_endpoint() -> None:
    r = client.get('/metrics')
    assert r.status_code == 200
    assert 'request_count' in r.json()
