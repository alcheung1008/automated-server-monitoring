# Automated Server Monitoring and Incident Response

## Group Information

Group Number: [Enter Group Number]

Group Members:

- [Member Name]
- [Member Name]
- [Member Name]

## Project Overview

This project provides an automated server-monitoring and incident-response system.

The system monitors a website and its PostgreSQL database using Prometheus. If the website becomes unavailable, Prometheus generates a website alert. If the database becomes unavailable, Prometheus detects the database failure and generates database-related alerts.

Alertmanager forwards alerts to a Python notification service, which sends notifications to a Webex room.

Jenkins automates testing, container building, and deployment. Docker Compose runs the website, database, monitoring, alerting, and notification components together.

## Technologies Used

- GitHub
- Jenkins
- GitHub webhooks or Jenkins polling
- Docker
- Docker Compose
- Python
- Flask
- Pytest
- PostgreSQL
- PostgreSQL Exporter
- Prometheus
- Alertmanager
- Webex API

## Project Architecture

```text
GitHub
   |
   | Push or Jenkins polling
   v
Jenkins
   |
   | Unit tests, image builds, and deployment
   v
Docker Compose
   |
   +-- Website container
   |       |
   |       +-- Health endpoint
   |       +-- Database connection
   |       +-- Prometheus metrics
   |
   +-- PostgreSQL database
   |
   +-- PostgreSQL Exporter
   |
   +-- Prometheus
   |
   +-- Alertmanager
   |
   +-- Python Webex notification service
                |
                | Webex API
                v
          Webex alert room
```

## Repository Structure

```text
automated-server-monitoring/
├── docker-compose.yml
├── Jenkinsfile
├── .env.example
├── .gitignore
├── README.md
│
├── prometheus/
│   ├── prometheus.yml
│   └── alert_rules.yml
│
├── alertmanager/
│   └── alertmanager.yml
│
├── notification-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       └── test_app.py
│
└── demo-target/
    ├── app.py
    ├── requirements.txt
    └── Dockerfile
```

## Prerequisites

The deployment host requires:

- Ubuntu Linux
- Git
- Docker Engine
- Docker Compose
- A Webex bot token
- A Webex room ID
- Jenkins for automated deployment

Verify Docker and Docker Compose:

```bash
docker --version
docker compose version
```

## Clone the Repository

```bash
git clone https://github.com/alcheung1008/automated-server-monitoring.git
cd automated-server-monitoring
```

## Configure Environment Variables

Create the environment file:

```bash
cp .env.example .env
```

Edit the file:

```bash
nano .env
```

Add the Webex and PostgreSQL values:

```env
WEBEX_BOT_TOKEN=your_webex_bot_token
WEBEX_ROOM_ID=your_webex_room_id

POSTGRES_DB=monitoring
POSTGRES_USER=monitor
POSTGRES_PASSWORD=monitor_password
```

The `.env` file contains sensitive credentials and must not be committed to GitHub.

Restrict the file permissions:

```bash
chmod 600 .env
```

Verify that Git ignores the file:

```bash
git check-ignore -v .env
```

## Start the Project

Build and start the complete application:

```bash
docker compose up -d --build
```

To force all containers to be recreated:

```bash
docker compose up -d --build --force-recreate
```

Check the container status:

```bash
docker compose ps
```

The following containers should be running:

```text
monitoring-database
demo-target
notification-service
prometheus
alertmanager
postgres-exporter
```

## Verify the Deployment

Test the website:

```bash
curl http://localhost:8000/
```

The website provides a monitoring dashboard showing the website and database status.

Test the website health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "database": "healthy",
  "website": "healthy"
}
```

Test the database-backed endpoint:

```bash
curl http://localhost:8000/data
```

Expected response:

```json
{
  "database": "monitoring",
  "message": "Database connection works"
}
```

Test the notification service:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Test Prometheus:

```bash
curl http://localhost:9090/-/ready
```

Expected response:

```text
Prometheus is Ready.
```

Test the PostgreSQL exporter:

```bash
curl http://localhost:9187/metrics | grep pg_up
```

Expected output:

```text
pg_up 1
```

View container logs:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop viewing logs. This does not stop the containers.

## Access the Services

When running directly on the deployment host:

| Service | URL |
|---|---|
| Website dashboard | `http://SERVER_IP:8000` |
| Website health endpoint | `http://SERVER_IP:8000/health` |
| Database test endpoint | `http://SERVER_IP:8000/data` |
| Website metrics | `http://SERVER_IP:8000/metrics` |
| Notification service | `http://SERVER_IP:5000/health` |
| Prometheus | `http://SERVER_IP:9090` |
| Alertmanager | `http://SERVER_IP:9093` |
| PostgreSQL exporter | `http://SERVER_IP:9187/metrics` |
| Jenkins | `http://SERVER_IP:8080` |

If the project is running inside a NAT-configured virtual machine, use port forwarding or an SSH tunnel.

When using the SSH tunnel, use:

```text
Website dashboard: http://localhost:8000
Prometheus: http://localhost:9090
Alertmanager: http://localhost:9093
Jenkins: http://localhost:8080
```

## Prometheus Monitoring

Open Prometheus:

```text
http://localhost:9090
```

Open the targets page:

```text
http://localhost:9090/targets
```

The following targets should show as `UP`:

```text
demo-target
database
```

The `database` target is backed by the PostgreSQL exporter.

The exporter exposes PostgreSQL metrics, including:

```text
pg_up
```

The metrics have two different meanings:

```text
up{job="database"}
```

This indicates whether Prometheus can reach the database metrics endpoint.

```text
pg_up{job="database"}
```

This indicates whether the PostgreSQL exporter can connect to the actual PostgreSQL database.

Query the website target:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="demo-target"}' | jq
```

Query the database target:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="database"}' | jq
```

Query the actual PostgreSQL health:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=pg_up{job="database"}' | jq
```

A healthy PostgreSQL database should return a value of:

```text
1
```

## Prometheus Alerts

The project includes alerts for:

- Website failure
- Database exporter failure
- PostgreSQL database failure
- Website-to-database connection failure

The alert names are:

```text
WebsiteDown
DatabaseExporterDown
DatabaseDown
WebsiteDatabaseConnectionFailed
```

## Simulating Website Downtime

Stop only the website container:

```bash
docker compose stop demo-target
```

Wait approximately 30 seconds for Prometheus to detect the failure.

Check the active alerts:

```bash
curl -s http://localhost:9090/api/v1/alerts | jq
```

A `WebsiteDown` alert should appear.

A Webex notification should also be sent identifying the website failure.

Check the notification service logs:

```bash
docker compose logs notification-service
```

Restore the website:

```bash
docker compose start demo-target
```

Wait for Prometheus and Alertmanager to detect the recovery. A resolved Webex notification should be sent.

## Simulating Database Downtime

Start the complete project first:

```bash
docker compose up -d
```

Stop only the PostgreSQL database:

```bash
docker compose stop database
```

The website container should remain running, but it should no longer be able to connect to PostgreSQL.

Check the website health endpoint:

```bash
curl -i http://localhost:8000/health
```

Expected response:

```json
{
  "database": "unhealthy",
  "website": "healthy"
}
```

The HTTP response should have status code `503`.

Check the website database metric:

```bash
curl -s http://localhost:8000/metrics | grep website_database_connection_up
```

Expected result:

```text
website_database_connection_up 0.0
```

Check the actual PostgreSQL metric:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=pg_up{job="database"}' | jq
```

The value should be:

```text
0
```

Wait approximately 30 seconds, then check Prometheus:

```bash
curl -s http://localhost:9090/api/v1/alerts | jq
```

The following alerts should appear:

```text
DatabaseDown
WebsiteDatabaseConnectionFailed
```

Webex notifications should identify the database-related failure.

Restore PostgreSQL:

```bash
docker compose start database
```

Verify the database recovered:

```bash
docker compose ps
```

Then test the website:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "database": "healthy",
  "website": "healthy"
}
```

A resolved Webex notification should eventually be sent.

## Run Unit Tests

Run the notification service tests:

```bash
docker compose run --rm --no-deps notification-service pytest -q
```

Expected result:

```text
2 passed
```

## Jenkins Deployment

Jenkins automates the testing and deployment process.

The Jenkins pipeline performs the following actions:

1. Checks out the GitHub repository.
2. Creates the `.env` file using Jenkins credentials.
3. Validates the Docker Compose configuration.
4. Builds the Docker images.
5. Runs the Python unit tests.
6. Starts the Docker Compose services.
7. Runs smoke tests.

## Jenkins Credentials

Create two Jenkins secret text credentials under:

```text
Manage Jenkins
→ Credentials
→ System
→ Global credentials
```

Create the Webex bot token credential:

```text
Kind: Secret text
ID: webex-bot-token
Secret: your Webex bot token
```

Create the Webex room ID credential:

```text
Kind: Secret text
ID: webex-room-id
Secret: your Webex room ID
```

The credential IDs must match the IDs used by the `Jenkinsfile`.

## Jenkins Pipeline Job

Create a Jenkins Pipeline job using:

```text
Repository URL:
https://github.com/alcheung1008/automated-server-monitoring.git
```

Configure the pipeline as:

```text
Definition: Pipeline script from SCM
SCM: Git
Branch: */main
Script Path: Jenkinsfile
```

Run the pipeline using:

```text
Build Now
```

A successful build should end with:

```text
Finished: SUCCESS
```

## GitHub Integration

If Jenkins can be reached from GitHub, configure a GitHub webhook using:

```text
http://JENKINS_SERVER_IP:8080/github-webhook/
```

If Jenkins is running on a private network and GitHub cannot reach it, use Jenkins polling instead.

In the Jenkins job configuration, enable:

```text
Poll SCM
```

Use the following schedule:

```text
H/5 * * * *
```

This checks the GitHub repository approximately every five minutes for changes.

You can also manually start a build using:

```text
Build Now
```

## Docker Commands

View running containers:

```bash
docker compose ps
```

View all logs:

```bash
docker compose logs -f
```

View logs for a specific service:

```bash
docker compose logs -f database
docker compose logs -f demo-target
docker compose logs -f postgres-exporter
docker compose logs -f prometheus
docker compose logs -f alertmanager
docker compose logs -f notification-service
```

Restart the services:

```bash
docker compose restart
```

Stop the services:

```bash
docker compose stop
```

Start stopped services:

```bash
docker compose start
```

Stop and remove the containers:

```bash
docker compose down
```

Stop and remove the containers while preserving database data:

```bash
docker compose down
```

Do not use the following command unless you intentionally want to delete the PostgreSQL data volume:

```bash
docker compose down -v
```

Rebuild the project:

```bash
docker compose down
docker compose up -d --build
```

## Troubleshooting

### The website container is not running

Check its status:

```bash
docker compose ps demo-target
```

View its logs:

```bash
docker compose logs demo-target
```

Rebuild the website image:

```bash
docker compose build --no-cache demo-target
docker compose up -d demo-target
```

### PostgreSQL is not running

Check the database status:

```bash
docker compose ps database
```

View the database logs:

```bash
docker compose logs database
```

Check whether the database is healthy:

```bash
docker inspect monitoring-database --format='{{json .State.Health}}' | jq
```

### The PostgreSQL exporter is not working

Check the exporter status:

```bash
docker compose ps postgres-exporter
```

View its logs:

```bash
docker compose logs postgres-exporter
```

Test its metrics endpoint:

```bash
curl http://localhost:9187/metrics | grep pg_up
```

### The website cannot connect to PostgreSQL

Check the website health endpoint:

```bash
curl -i http://localhost:8000/health
```

Check the website logs:

```bash
docker compose logs demo-target
```

Verify that the database container is running:

```bash
docker compose ps database
```

Verify the database connection metric:

```bash
curl -s http://localhost:8000/metrics | grep website_database_connection_up
```

### Webex notifications are not received

Check the notification service logs:

```bash
docker compose logs notification-service
```

Verify that `.env` contains:

```env
WEBEX_BOT_TOKEN=your_webex_bot_token
WEBEX_ROOM_ID=your_webex_room_id
```

Verify that the Webex bot is a member of the alert room.

### Jenkins cannot run Docker commands

Check whether the Jenkins user belongs to the Docker group:

```bash
groups jenkins
```

If necessary:

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Jenkins tests fail

Run the tests manually:

```bash
docker compose run --rm --no-deps notification-service pytest -q
```

Rebuild the notification service image:

```bash
docker compose build --no-cache notification-service
```

## Project Outcome

The completed system demonstrates this automated workflow:

```text
GitHub code change
        ↓
Jenkins pipeline
        ↓
Unit tests
        ↓
Docker deployment
        ↓
Website and database monitoring
        ↓
Prometheus alert rules
        ↓
Alertmanager
        ↓
Python notification service
        ↓
Webex incident notification
```
