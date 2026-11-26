import os
from datetime import datetime, timezone

import psycopg2
from flask import Flask, Response, jsonify, render_template_string
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    generate_latest,
)

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "demo_target_requests_total",
    "Total number of requests received by the demo target",
)

DATABASE_CONNECTION = Gauge(
    "website_database_connection_up",
    "Whether the website can connect to PostgreSQL",
)


def get_database_settings():
    return {
        "host": os.getenv("DATABASE_HOST", "database"),
        "port": os.getenv("DATABASE_PORT", "5432"),
        "dbname": os.getenv("DATABASE_NAME", "monitoring"),
        "user": os.getenv("DATABASE_USER", "monitor"),
        "password": os.getenv("DATABASE_PASSWORD", "monitor_password"),
        "connect_timeout": 2,
    }


def check_database():
    try:
        with psycopg2.connect(**get_database_settings()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return True

    except Exception as error:
        app.logger.warning("Database check failed: %s", error)
        return False


def get_database_name():
    try:
        with psycopg2.connect(**get_database_settings()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                return cursor.fetchone()[0]

    except Exception:
        return None


@app.before_request
def count_request():
    REQUEST_COUNT.inc()


@app.route("/")
def index():
    database_healthy = check_database()
    database_name = get_database_name() if database_healthy else None

    DATABASE_CONNECTION.set(1 if database_healthy else 0)

    website_status = "Operational"
    database_status = "Connected" if database_healthy else "Unavailable"
    status_class = "healthy" if database_healthy else "unhealthy"

    return render_template_string(
        """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infrastructure Monitor</title>

    <style>
        :root {
            color-scheme: dark;
            --background: #0f172a;
            --panel: #1e293b;
            --panel-light: #334155;
            --text: #f8fafc;
            --muted: #94a3b8;
            --blue: #38bdf8;
            --green: #22c55e;
            --red: #ef4444;
            --border: rgba(148, 163, 184, 0.2);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, #164e63 0, transparent 35%),
                linear-gradient(135deg, #0f172a, #111827 60%, #172554);
        }

        .container {
            width: min(1100px, 92%);
            margin: 0 auto;
            padding: 48px 0;
        }

        .hero {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 24px;
            margin-bottom: 32px;
        }

        .eyebrow {
            margin: 0 0 10px;
            color: var(--blue);
            font-size: 0.8rem;
            font-weight: bold;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        h1 {
            margin: 0;
            font-size: clamp(2.2rem, 5vw, 4rem);
            line-height: 1;
        }

        .subtitle {
            max-width: 650px;
            margin-top: 16px;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.6;
        }

        .logo {
            display: grid;
            width: 86px;
            height: 86px;
            place-items: center;
            border: 1px solid rgba(56, 189, 248, 0.5);
            border-radius: 24px;
            color: var(--blue);
            background: rgba(56, 189, 248, 0.1);
            box-shadow: 0 0 40px rgba(56, 189, 248, 0.15);
            font-size: 2.6rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
        }

        .card {
            padding: 24px;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: rgba(30, 41, 59, 0.82);
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
        }

        .card h2 {
            margin: 0 0 12px;
            font-size: 1.1rem;
        }

        .card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.5;
        }

        .status-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 22px;
        }

        .indicator {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            box-shadow: 0 0 18px currentColor;
        }

        .healthy {
            color: var(--green);
        }

        .unhealthy {
            color: var(--red);
        }

        .status-text {
            font-size: 1.25rem;
            font-weight: bold;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            padding: 14px 0;
            border-bottom: 1px solid var(--border);
        }

        .metric:last-child {
            border-bottom: 0;
        }

        .metric-label {
            color: var(--muted);
        }

        .metric-value {
            font-weight: bold;
            text-align: right;
        }

        .links {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 20px;
        }

        .links a {
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text);
            background: rgba(51, 65, 85, 0.7);
            text-decoration: none;
        }

        .links a:hover {
            border-color: var(--blue);
            color: var(--blue);
        }

        footer {
            margin-top: 28px;
            color: var(--muted);
            font-size: 0.9rem;
            text-align: center;
        }

        @media (max-width: 700px) {
            .hero {
                align-items: flex-start;
            }

            .logo {
                display: none;
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
    <main class="container">
        <section class="hero">
            <div>
                <p class="eyebrow">Automated Server Monitoring</p>
                <h1>Infrastructure Monitor</h1>
                <p class="subtitle">
                    A Dockerized monitoring application powered by Prometheus,
                    Alertmanager, PostgreSQL, Jenkins, and Webex notifications.
                </p>
            </div>

            <div class="logo">⌁</div>
        </section>

        <section class="grid">
            <article class="card">
                <h2>Website Status</h2>
                <p>
                    The monitoring dashboard is running and responding to requests.
                </p>

                <div class="status-row {{ status_class }}">
                    <span class="indicator"></span>
                    <span class="status-text">{{ website_status }}</span>
                </div>
            </article>

            <article class="card">
                <h2>Database Status</h2>
                <p>
                    The website performs a live PostgreSQL connectivity check.
                </p>

                <div class="status-row {{ status_class }}">
                    <span class="indicator"></span>
                    <span class="status-text">{{ database_status }}</span>
                </div>
            </article>

            <article class="card">
                <h2>System Details</h2>

                <div class="metric">
                    <span class="metric-label">Database</span>
                    <span class="metric-value">
                        {{ database_name or "Unavailable" }}
                    </span>
                </div>

                <div class="metric">
                    <span class="metric-label">Monitoring</span>
                    <span class="metric-value">Prometheus</span>
                </div>

                <div class="metric">
                    <span class="metric-label">Notifications</span>
                    <span class="metric-value">Webex</span>
                </div>

                <div class="metric">
                    <span class="metric-label">Updated</span>
                    <span class="metric-value">{{ timestamp }}</span>
                </div>
            </article>

            <article class="card">
                <h2>Monitoring Endpoints</h2>
                <p>
                    These endpoints are used by Prometheus and the monitoring workflow.
                </p>

                <div class="links">
                    <a href="/health">Health Check</a>
                    <a href="/data">Database Test</a>
                    <a href="/metrics">Prometheus Metrics</a>
                </div>
            </article>
        </section>

        <footer>
            Automated Server Monitoring and Incident Response
        </footer>
    </main>
</body>
</html>
        """,
        database_name=database_name,
        database_status=database_status,
        status_class=status_class,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        website_status=website_status,
    )


@app.route("/health")
def health():
    database_healthy = check_database()

    DATABASE_CONNECTION.set(1 if database_healthy else 0)

    response = {
        "website": "healthy",
        "database": "healthy" if database_healthy else "unhealthy",
    }

    if database_healthy:
        return jsonify(response), 200

    return jsonify(response), 503


@app.route("/data")
def data():
    database_name = get_database_name()

    if database_name is None:
        return jsonify({
            "error": "The website cannot connect to the database"
        }), 503

    return jsonify({
        "message": "Database connection works",
        "database": database_name,
    })


@app.route("/metrics")
def metrics():
    database_healthy = check_database()

    DATABASE_CONNECTION.set(1 if database_healthy else 0)

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
