from pymongo import MongoClient
import json
import os
def run_mapreduce(mongo_uri, db_name, out_file):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    coll = db["taxi_trips"]

    map_js = """
        function() {
            emit({grid_key: this.grid_key, hour: this.hour}, 
                 {count: 1, fare_sum: this.fare_amount, dist_sum: this.trip_distance});
        }
    """
    reduce_js = """
        function(key, values) {
            let res = {count: 0, fare_sum: 0, dist_sum: 0};
            values.forEach(v => {
                res.count += v.count;
                res.fare_sum += v.fare_sum;
                res.dist_sum += v.dist_sum;
            });
            return res;
        }
    """
    finalize_js = """
        function(key, value) {
            value.avg_fare = value.fare_sum / value.count;
            value.avg_distance = value.dist_sum / value.count;
            return value;
        }
    """

    result = db.command({
        "mapReduce": "taxi_trips",
        "map": map_js,
        "reduce": reduce_js,
        "finalize": finalize_js,
        "out": {"inline": 1}
    })

    docs = []
    for r in result["results"]:
        k = r["_id"]
        v = r["value"]
        docs.append({
            "grid_key": k["grid_key"],
            "hour": k["hour"],
            "count": v["count"],
            "avg_fare": v["avg_fare"],
            "avg_distance": v["avg_distance"]
        })
    os.makedirs(os.path.dirname(out_file), exist_ok=True)    

    with open(out_file, "w") as f:
        json.dump(docs, f, indent=2)
    print(f"MapReduce complete: {len(docs)} rows → {out_file}")
    return docs
