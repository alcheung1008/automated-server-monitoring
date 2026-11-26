from app import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_alert_endpoint():
    client = app.test_client()

    payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "TestAlert",
                    "severity": "warning",
                },
                "annotations": {
                    "summary": "Test alert",
                    "description": "This is a test alert.",
                },
            }
        ]
    }

    response = client.post("/alert", json=payload)

    assert response.status_code == 200
    assert response.json["received_alerts"] == 1
