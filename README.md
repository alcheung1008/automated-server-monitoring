# Automated Server Monitoring and Incident Response

## Overview

This project monitors a demo service using Prometheus. When the service becomes unavailable, Prometheus generates an alert. Alertmanager forwards the alert to a Python notification service, which sends a notification to a Webex room.

Jenkins automatically validates, tests, builds, and deploys the system using Docker Compose.

## Technologies

- GitHub
- GitHub Webhooks
- Jenkins
- Docker
- Docker Compose
- Python
- Pytest
- Prometheus
- Alertmanager
- Webex API

## Start the Project

Create a `.env` file containing:

```env
WEBEX_BOT_TOKEN=your_token
WEBEX_ROOM_ID=your_room_id
