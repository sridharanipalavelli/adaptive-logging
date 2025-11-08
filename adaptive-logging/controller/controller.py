import os
import time
import requests

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
APP_SERVICE_URL = os.getenv("APP_SERVICE_URL", "http://adaptive-app:5000")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "15"))  # seconds
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "0.05"))  # errors per req (example)
WINDOW = os.getenv("WINDOW", "1m")  # PromQL range or instant as needed

def query_prometheus(expr):
    url = PROMETHEUS_URL.rstrip("/") + "/api/v1/query"
    resp = requests.get(url, params={"query": expr}, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return data

def get_error_ratio():
    # Example PromQL: increase(app_errors_total[1m]) / increase(app_requests_total[1m])
    expr = f'increase(app_errors_total[{WINDOW}]) / increase(app_requests_total[{WINDOW}])'
    try:
        data = query_prometheus(expr)
        result = data.get("data", {}).get("result", [])
        if not result:
            return 0.0
        val = float(result[0]["value"][1])
        return val
    except Exception as e:
        print("Prometheus query failed:", e)
        return 0.0

def set_log_level(level):
    try:
        resp = requests.post(APP_SERVICE_URL.rstrip("/") + "/set_log", json={"level": level}, timeout=5)
        print("set_log response:", resp.status_code, resp.text)
    except Exception as e:
        print("Failed to set log level:", e)

if __name__ == "__main__":
    current = "INFO"
    set_log_level(current)
    while True:
        ratio = get_error_ratio()
        print("error ratio:", ratio)
        if ratio >= ERROR_RATE_THRESHOLD and current != "DEBUG":
            print("High error ratio -> switching to DEBUG")
            set_log_level("DEBUG")
            current = "DEBUG"
        elif ratio < ERROR_RATE_THRESHOLD and current != "INFO":
            print("Error ratio low -> switching to INFO")
            set_log_level("INFO")
            current = "INFO"
        time.sleep(CHECK_INTERVAL)
