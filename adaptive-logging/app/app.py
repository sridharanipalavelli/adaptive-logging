from flask import Flask, request, jsonify
import logging
from prometheus_client import Counter, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)

# Logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)
logger = logging.getLogger("adaptive_app")
logger.setLevel(numeric_level)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# Prometheus counters
REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
ERROR_COUNT = Counter('app_errors_total', 'Total errors')

@app.route("/")
def index():
    REQUEST_COUNT.inc()
    logger.info("Index accessed")
    return jsonify({"message": "Adaptive logging demo", "log_level": logging.getLevelName(logger.level)})

@app.route("/error")
def error():
    REQUEST_COUNT.inc()
    ERROR_COUNT.inc()
    logger.error("Simulated error endpoint hit")
    return jsonify({"message": "error generated"}), 500

@app.route("/set_log", methods=["POST"])
def set_log():
    """
    Set runtime log level. POST JSON: {"level": "DEBUG"}
    """
    data = request.get_json() or {}
    level = (data.get("level") or "").upper()
    if level not in ("DEBUG","INFO","WARNING","ERROR","CRITICAL"):
        return jsonify({"error":"invalid level"}), 400
    logger.setLevel(getattr(logging, level))
    return jsonify({"message":"log level set", "level": level})

# Expose /metrics via prometheus_client
@app.route("/metrics")
def metrics():
    resp = generate_latest()
    return resp, 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
