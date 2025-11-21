# from flask import Flask, jsonify, request, send_from_directory
# import os
# import sys
# # ensure project root (where scripts/ lives) is in sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from scripts.ingest import ingest_data
# from scripts.aggregate import run_aggregation
# from scripts.mapreduce import run_mapreduce
# from scripts.postprocess import detect_anomalies

# app = Flask(__name__)

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("MONGO_DB", "taxi_hotspot_db")
# CSV_PATH = "/home/prajwal-ca/Desktop/taxi-hotspot-analytics/taxi-hotspot-analytics/data/raw/yellow_tripdata_2019-01.csv"

# AGG_JSON = "data/results/hourly_grid_counts.json"
# MR_JSON = "data/results/mapreduce_hourly_grid_counts.json"
# ANOM_JSON = "data/results/anomaly_cells.json"

# # --- initialize pipeline ---
# print("🚀 Starting full pipeline...")

# ingest_data(CSV_PATH, MONGO_URI, DB_NAME, sample_rows=5000, drop=True)
# run_aggregation(MONGO_URI, DB_NAME, AGG_JSON)
# run_mapreduce(MONGO_URI, DB_NAME, MR_JSON)
# detect_anomalies(AGG_JSON, ANOM_JSON)

# print("✅ All processing done. Launching API...")

# @app.route("/api/hotspots")
# def get_hotspots():
#     hour = int(request.args.get("hour", 0))
#     import json
#     with open(AGG_JSON) as f:
#         data = json.load(f)
#     return jsonify([d for d in data if d["hour"] == hour])

# @app.route("/api/anomalies")
# def get_anomalies():
#     import json
#     with open(ANOM_JSON) as f:
#         return jsonify(json.load(f))

# @app.route("/")
# def index():
#     return send_from_directory("../frontend", "index.html")

# if __name__ == "__main__":
#     app.run(debug=True)
#!/usr/bin/env python3
import os
import sys

# ensure project root is on path so "scripts" imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path

# imports from your scripts (they must exist in scripts/)
from scripts.ingest import ingest_data
from scripts.aggregate import run_aggregation
from scripts.mapreduce import run_mapreduce
from scripts.postprocess import detect_anomalies

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "taxi_hotspot_db")

# Frontend folder (project_root/frontend)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DATA_RESULTS = os.path.join(PROJECT_ROOT, "data", "results")
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "yellow_tripdata_2019-01.csv")

AGG_JSON = os.path.join(DATA_RESULTS, "hourly_grid_counts.json")
MR_JSON  = os.path.join(DATA_RESULTS, "mapreduce_hourly_grid_counts.json")
ANOM_JSON = os.path.join(DATA_RESULTS, "anomaly_cells.json")

# Create the Flask app and configure static folder to serve frontend
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,   # serve static files from project_root/frontend
    static_url_path="/static"     # they will be available at /static/<file>
)

@app.route("/")
def index():
    # Serve index.html from frontend folder (via send_from_directory)
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/hotspots")
def api_hotspots():
    hour = request.args.get("hour", default=None, type=int)
    if not os.path.exists(AGG_JSON):
        return jsonify({"error":"aggregation file not found"}), 500
    import json
    with open(AGG_JSON) as f:
        data = json.load(f)
    if hour is not None:
        data = [d for d in data if int(d.get("hour", -1)) == hour]
    return jsonify(data)

@app.route("/api/anomalies")
def api_anomalies():
    if not os.path.exists(ANOM_JSON):
        return jsonify([])
    import json
    with open(ANOM_JSON) as f:
        return jsonify(json.load(f))

def ensure_results_dir():
    Path(DATA_RESULTS).mkdir(parents=True, exist_ok=True)

# def run_full_pipeline(sample_rows=5000, drop=True):
#     ensure_results_dir()
#     print("1) Ingesting CSV into MongoDB...")
#     inserted = ingest_data(CSV_PATH, MONGO_URI, DB_NAME, sample_rows=sample_rows, drop=drop)
#     print(f"Inserted {inserted} rows.")
#     print("2) Running aggregation...")
#     run_aggregation(MONGO_URI, DB_NAME, AGG_JSON)
#     print("3) Running map-reduce...")
#     run_mapreduce(MONGO_URI, DB_NAME, MR_JSON)
#     print("4) Detecting anomalies...")
#     detect_anomalies(AGG_JSON, ANOM_JSON)
#     print("Pipeline complete.")
import time, json

def run_full_pipeline(sample_rows=5000, drop=True):
    ensure_results_dir()
    t0 = time.time()
    print("1) Ingesting CSV...")
    ingest_data(CSV_PATH, MONGO_URI, DB_NAME, sample_rows=sample_rows, drop=drop)
    t1 = time.time()
    print("2) Aggregation...")
    start = time.time()
    run_aggregation(MONGO_URI, DB_NAME, AGG_JSON)
    t2 = time.time()
    print("3) MapReduce...")
    run_mapreduce(MONGO_URI, DB_NAME, MR_JSON)
    t3 = time.time()
    detect_anomalies(AGG_JSON, ANOM_JSON)
    t4 = time.time()

    times = {
        "ingest_time": round(t1 - t0, 3),
        "aggregation_time": round(t2 - start, 3),
        "mapreduce_time": round(t3 - t2, 3),
        "anomaly_time": round(t4 - t3, 3)
    }
    json.dump(times, open(os.path.join(DATA_RESULTS, "timing.json"), "w"), indent=2)
    print("Timing results saved:", times)

if __name__ == "__main__":
    # Only run the pipeline on first start (or you can disable)
    # If you want to skip running pipeline every time, change drop=False or remove run_full_pipeline
    run_full_pipeline(sample_rows=5000, drop=True)
    print("Starting Flask server on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
