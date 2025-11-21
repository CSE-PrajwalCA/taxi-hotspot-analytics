from pymongo import MongoClient
import json

def run_aggregation(mongo_uri, db_name, out_file):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    pipeline = [
        {"$group": {
            "_id": {"grid_key": "$grid_key", "hour": "$hour"},
            "count": {"$sum": 1},
            "avg_fare": {"$avg": "$fare_amount"},
            "avg_distance": {"$avg": "$trip_distance"},
            "grid_x": {"$first": "$grid_x"},
            "grid_y": {"$first": "$grid_y"}
        }},
        {"$project": {
            "_id": 0,
            "grid_key": "$_id.grid_key",
            "hour": "$_id.hour",
            "count": 1, "avg_fare": 1, "avg_distance": 1,
            "grid_x": 1, "grid_y": 1
        }}
    ]

    result = list(db["taxi_trips"].aggregate(pipeline))
    import os

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Aggregation complete: {len(result)} rows → {out_file}")
    return result
