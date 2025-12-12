import json

from app import create_app


def test_metrics_endpoint():
    app = create_app()
    client = app.test_client()

    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = json.loads(resp.data.decode("utf-8"))
    assert "metrics" in data
    assert isinstance(data["metrics"], list)
    assert any(m["id"] == "total_revenue" for m in data["metrics"])


def test_chart_endpoint():
    app = create_app()
    client = app.test_client()

    resp = client.get("/api/charts/revenue_over_time")
    assert resp.status_code == 200
    data = json.loads(resp.data.decode("utf-8"))
    assert data["id"] == "revenue_over_time"
    assert "points" in data
    assert isinstance(data["points"], list)
