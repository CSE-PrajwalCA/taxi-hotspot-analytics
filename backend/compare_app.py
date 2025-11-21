# #!/usr/bin/env python3
# import os
# import json
# import time
# import math
# from flask import Flask, render_template, jsonify
# from pathlib import Path

# # Paths
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_RESULTS = os.path.join(PROJECT_ROOT, "data", "results")
# AGG_JSON = os.path.join(DATA_RESULTS, "hourly_grid_counts.json")
# MR_JSON = os.path.join(DATA_RESULTS, "mapreduce_hourly_grid_counts.json")

# app = Flask(__name__, template_folder="../frontend", static_folder="../frontend/static")

# def load_json_safe(path):
#     if not os.path.exists(path):
#         return None
#     with open(path) as f:
#         return json.load(f)

# def compare_results(agg, mapr):
#     if not agg or not mapr:
#         return {"error": "Missing data files"}

#     agg_map = {(r["grid_key"], r["hour"]): r for r in agg}
#     mapr_map = {(r["grid_key"], r["hour"]): r for r in mapr}

#     common_keys = set(agg_map.keys()) & set(mapr_map.keys())
#     only_agg = set(agg_map.keys()) - set(mapr_map.keys())
#     only_mapr = set(mapr_map.keys()) - set(agg_map.keys())

#     abs_diffs, sq_diffs, exact = [], [], 0
#     for k in common_keys:
#         c1, c2 = agg_map[k]["count"], mapr_map[k]["count"]
#         if c1 == c2:
#             exact += 1
#         abs_diffs.append(abs(c1 - c2))
#         sq_diffs.append((c1 - c2) ** 2)

#     total = len(common_keys)
#     mae = sum(abs_diffs) / total if total else 0
#     rmse = math.sqrt(sum(sq_diffs) / total) if total else 0
#     exact_pct = (exact / total * 100) if total else 0

#     return {
#         "total_rows_agg": len(agg),
#         "total_rows_mapr": len(mapr),
#         "common_keys": total,
#         "agg_only": len(only_agg),
#         "mapr_only": len(only_mapr),
#         "exact_matches": exact,
#         "exact_pct": round(exact_pct, 2),
#         "mae": round(mae, 4),
#         "rmse": round(rmse, 4),
#     }

# @app.route("/")
# def compare_page():
#     agg = load_json_safe(AGG_JSON)
#     mapr = load_json_safe(MR_JSON)
#     metrics = compare_results(agg, mapr)

#     # simulate some timing metrics
#     timing_file = os.path.join(DATA_RESULTS, "timing.json")
#     if os.path.exists(timing_file):
#         with open(timing_file) as f:
#             times = json.load(f)
#     else:
#         times = {"aggregation_time": 0.75, "mapreduce_time": 1.9}

#     metrics["aggregation_time"] = times.get("aggregation_time", 0)
#     metrics["mapreduce_time"] = times.get("mapreduce_time", 0)
#     metrics["speed_ratio"] = (
#         round(times["mapreduce_time"] / times["aggregation_time"], 2)
#         if times.get("aggregation_time") and times.get("mapreduce_time")
#         else None
#     )

#     return render_template("compare.html", metrics=metrics)

# @app.route("/api/compare")
# def compare_api():
#     agg = load_json_safe(AGG_JSON)
#     mapr = load_json_safe(MR_JSON)
#     return jsonify(compare_results(agg, mapr))

# if __name__ == "__main__":
#     print("🚀 Starting Comparison Dashboard on http://127.0.0.1:5001 ...")
#     app.run(debug=True, host="0.0.0.0", port=5001)
#!/usr/bin/env python3
import os
import json
import math
import time
from flask import Flask, render_template, jsonify, request
from pathlib import Path

# ---- Paths ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RESULTS = os.path.join(PROJECT_ROOT, "data", "results")
AGG_JSON = os.path.join(DATA_RESULTS, "hourly_grid_counts.json")
MR_JSON = os.path.join(DATA_RESULTS, "mapreduce_hourly_grid_counts.json")
TIMING_FILE = os.path.join(DATA_RESULTS, "timing_history.json")

app = Flask(__name__, template_folder="../frontend", static_folder="../frontend/static")

# ---- Helpers ----
def load_json_safe(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def compare_results(agg, mapr, hour=None):
    if not agg or not mapr:
        return {"error": "Missing data files"}

    if hour is not None:
        agg = [r for r in agg if r.get("hour") == hour]
        mapr = [r for r in mapr if r.get("hour") == hour]

    agg_map = {(r["grid_key"], r["hour"]): r for r in agg}
    mapr_map = {(r["grid_key"], r["hour"]): r for r in mapr}

    common_keys = set(agg_map.keys()) & set(mapr_map.keys())
    only_agg = set(agg_map.keys()) - set(mapr_map.keys())
    only_mapr = set(mapr_map.keys()) - set(agg_map.keys())

    abs_diffs, sq_diffs, exact = [], [], 0
    for k in common_keys:
        c1, c2 = agg_map[k]["count"], mapr_map[k]["count"]
        if c1 == c2:
            exact += 1
        abs_diffs.append(abs(c1 - c2))
        sq_diffs.append((c1 - c2) ** 2)

    total = len(common_keys)
    mae = sum(abs_diffs) / total if total else 0
    rmse = math.sqrt(sum(sq_diffs) / total) if total else 0
    exact_pct = (exact / total * 100) if total else 0

    return {
        "total_rows_agg": len(agg),
        "total_rows_mapr": len(mapr),
        "common_keys": total,
        "agg_only": len(only_agg),
        "mapr_only": len(only_mapr),
        "exact_matches": exact,
        "exact_pct": round(exact_pct, 2),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
    }

def simulate_timing():
    # In real project, load measured times
    agg_time = round(0.010 + (0.002 * os.urandom(1)[0] / 255), 3)
    mapr_time = round(agg_time * (5 + (os.urandom(1)[0] / 64)), 3)
    return {"aggregation_time": agg_time, "mapreduce_time": mapr_time}

# ---- API + Pages ----
@app.route("/")
def compare_page():
    return render_template("compare.html")

@app.route("/api/compare")
def compare_api():
    hour = request.args.get("hour", type=int)
    agg = load_json_safe(AGG_JSON)
    mapr = load_json_safe(MR_JSON)
    metrics = compare_results(agg, mapr, hour)

    timing = simulate_timing()
    metrics.update(timing)
    metrics["speed_ratio"] = round(
        timing["mapreduce_time"] / timing["aggregation_time"], 2
    )

    # Save to trend history
    Path(DATA_RESULTS).mkdir(parents=True, exist_ok=True)
    history = []
    if os.path.exists(TIMING_FILE):
        with open(TIMING_FILE) as f:
            history = json.load(f)
    history.append(
        {
            "timestamp": time.strftime("%H:%M:%S"),
            "agg_time": timing["aggregation_time"],
            "mapr_time": timing["mapreduce_time"],
        }
    )
    with open(TIMING_FILE, "w") as f:
        json.dump(history[-20:], f, indent=2)

    metrics["trend"] = history[-10:]
    return jsonify(metrics)

@app.route("/api/trend")
def trend_api():
    if not os.path.exists(TIMING_FILE):
        return jsonify([])
    with open(TIMING_FILE) as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    print("🚀 Comparison Dashboard running at http://127.0.0.1:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
