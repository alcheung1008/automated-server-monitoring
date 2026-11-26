# Automated Server Monitoring and Incident Response

## Group Information

Group Number: [Enter Group Number]

Group Members:

- [Member Name]
- [Member Name]
- [Member Name]

## Project Overview

This project provides an automated server-monitoring and incident-response system.

The system monitors a demo service using Prometheus. If the monitored service becomes unavailable, Prometheus detects the failure and sends an alert to Alertmanager. Alertmanager forwards the alert to a Python notification service, which sends a notification to a Webex room.

Jenkins automates the testing, building, and deployment process. Docker Compose runs the project components in separate containers.

## Technologies Used

- GitHub
- Git webhooks or Jenkins polling
- Jenkins
- Docker
- Docker Compose
- Python
- Flask
- Pytest
- Prometheus
- Alertmanager
- Webex API

## Project Architecture

```text
GitHub
   |
   | Push or polling
   v
Jenkins
   |
   | Tests and deployment
   v
Docker Compose
   |
   +-- Demo target service
   |
   +-- Prometheus
   |
   +-- Alertmanager
   |
   +-- Python notification service
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

The deployment system requires:

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

## Configure Webex Credentials

Create the environment file from the example:

```bash
cp .env.example .env
```

Edit the file:

```bash
nano .env
```

Add the Webex bot token and room ID:

```env
WEBEX_BOT_TOKEN=your_webex_bot_token
WEBEX_ROOM_ID=your_webex_room_id
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

## Start the Project Manually

Build and start the containers:

```bash
docker compose up -d --build
```

Check the container status:

```bash
docker compose ps
```

The following containers should be running:

```text
demo-target
notification-service
prometheus
alertmanager
```

## Verify the Deployment

Test the demo target service:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

Test the notification service:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{"status":"healthy"}
```

Test Prometheus:

```bash
curl http://localhost:9090/-/ready
```

Expected response:

```text
Prometheus is Ready.
```

View the container logs:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop viewing the logs. This does not stop the containers.

## Access the Services

When running directly on the deployment system, the services are available at:

| Service | URL |
|---|---|
| Demo target | `http://SERVER_IP:8000` |
| Notification service | `http://SERVER_IP:5000/health` |
| Prometheus | `http://SERVER_IP:9090` |
| Alertmanager | `http://SERVER_IP:9093` |
| Jenkins | `http://SERVER_IP:8080` |

When using an SSH tunnel, use:

```text
Jenkins: http://localhost:8080
Prometheus: http://localhost:9090
Alertmanager: http://localhost:9093
Demo target: http://localhost:8000
Notification service: http://localhost:5000/health
```

## Verify Prometheus Monitoring

Open Prometheus in a browser:

```text
http://localhost:9090
```

Select:

```text
Status → Target health
```

The `demo-target` should show a status of `UP`.

The target can also be checked through the Prometheus API:

```bash
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="demo-target"}' | jq
```

A healthy target should return a value of `1`.

## Test the Alert Workflow

Stop the monitored demo service:

```bash
docker compose stop demo-target
```

Prometheus checks the service every few seconds. After the configured alert period, it should detect that the service is unavailable.

Check the current alerts:

```bash
curl -s http://localhost:9090/api/v1/alerts | jq
```

Check the notification service logs:

```bash
docker compose logs notification-service
```

A Webex notification should be sent to the configured room.

The alert should contain information similar to:

```text
Prometheus Alert: DemoTargetDown
Status: FIRING
Severity: critical
Summary: Demo target service is unavailable
```

Restore the monitored service:

```bash
docker compose start demo-target
```

After Prometheus detects the recovery, Alertmanager should send a resolved notification to Webex.

## Run Unit Tests

Run the notification service tests:

```bash
docker compose run --rm --no-deps notification-service pytest -q
```

The tests should complete successfully.

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
7. Runs smoke tests against the services.

## Jenkins Credentials

Jenkins requires two secret text credentials.

Create these credentials under:

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

The credential IDs must match the IDs used in the `Jenkinsfile`.

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

A manual build can also be started with:

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

View logs for one service:

```bash
docker compose logs -f prometheus
docker compose logs -f alertmanager
docker compose logs -f notification-service
docker compose logs -f demo-target
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

Rebuild the project:

```bash
docker compose down
docker compose up -d --build
```

## Troubleshooting

### Containers are not running

Check the container status:

```bash
docker compose ps
```

Check the logs:

```bash
docker compose logs
```

### Prometheus cannot scrape the demo target

Check the Prometheus target status:

```text
http://localhost:9090/targets
```

Check the demo target directly:

```bash
curl http://localhost:8000/metrics
```

### Webex notifications are not received

Check the notification service logs:

```bash
docker compose logs notification-service
```

Verify that the `.env` file contains:

```env
WEBEX_BOT_TOKEN=your_webex_bot_token
WEBEX_ROOM_ID=your_webex_room_id
```

Verify that the Webex bot is a member of the alert room.

### Jenkins cannot run Docker commands

Check that the Jenkins user belongs to the Docker group:

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

The completed system demonstrates an automated DevOps workflow:

```text
GitHub code change
        ↓
Jenkins pipeline
        ↓
Unit tests
        ↓
Docker deployment
        ↓
Prometheus monitoring
        ↓
Alertmanager alert processing
        ↓
Python notification service
        ↓
Webex incident notification
```
