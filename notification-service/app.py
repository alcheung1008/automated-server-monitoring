import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID", "")


def send_webex_message(message):
    if not WEBEX_BOT_TOKEN or not WEBEX_ROOM_ID:
        app.logger.warning(
            "Webex credentials are not configured. Message was not sent."
        )
        app.logger.info("Message: %s", message)
        return False

    response = requests.post(
        "https://webexapis.com/v1/messages",
        headers={
            "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "roomId": WEBEX_ROOM_ID,
            "text": message,
        },
        timeout=15,
    )

    response.raise_for_status()
    return True


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/alert", methods=["POST"])
def receive_alert():
    payload = request.get_json(silent=True) or {}
    alerts = payload.get("alerts", [])

    for alert in alerts:
        status = alert.get("status", "unknown").upper()
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        alert_name = labels.get("alertname", "Unknown alert")
        severity = labels.get("severity", "unknown")
        summary = annotations.get("summary", "No summary provided")
        description = annotations.get(
            "description",
            "No description provided"
        )

        message = (
            f"Prometheus Alert: {alert_name}\n"
            f"Status: {status}\n"
            f"Severity: {severity}\n"
            f"Summary: {summary}\n"
            f"Details: {description}"
        )

        try:
            send_webex_message(message)
        except requests.RequestException as error:
            app.logger.error("Webex request failed: %s", error)

    return jsonify({"received_alerts": len(alerts)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
