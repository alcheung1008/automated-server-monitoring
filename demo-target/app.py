from flask import Flask, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "demo_target_requests_total",
    "Total number of requests received by the demo target"
)


@app.before_request
def count_request():
    REQUEST_COUNT.inc()


@app.route("/")
def index():
    return "Demo target service is running\n"


@app.route("/health")
def health():
    return {"status": "healthy"}


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
