# Adaptive Logging - Prototype

This repository contains a simple prototype for adaptive logging level control:
- `app/` - Flask application exposing runtime log level change and Prometheus metrics
- `controller/` - Rule-based controller that queries Prometheus and toggles log level
- `k8s/` - Example Kubernetes manifests
- `docker-compose.yml` - For local testing
- `.github/workflows/ci-cd.yml` - GitHub Actions for build & deploy

See the project report for full design details.
