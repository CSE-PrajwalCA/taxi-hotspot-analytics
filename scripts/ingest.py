import pandas as pd
import math
import argparse
import os
from pymongo import MongoClient, ASCENDING, GEOSPHERE

# Load NYC taxi zone coordinates mapping
def load_zone_mapping():
    """Load PULocationID to lat/lon mapping from taxi zones file"""
    zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "data", "raw", "nyc_taxi_zones.csv")
    if not os.path.exists(zones_file):
        raise FileNotFoundError(f"NYC taxi zones mapping file not found: {zones_file}")
    
    zones_df = pd.read_csv(zones_file)
    # Create a mapping dictionary: LocationID -> (Latitude, Longitude)
    zone_mapping = {}
    for _, row in zones_df.iterrows():
        location_id = int(row['LocationID'])
        zone_mapping[location_id] = (float(row['Latitude']), float(row['Longitude']))
    return zone_mapping

def ingest_data(csv_path, mongo_uri, db_name, sample_rows=None, drop=False):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    coll = db["taxi_trips"]

    if drop:
        coll.drop()

    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, nrows=sample_rows)

    # Check if required columns exist
    if "tpep_pickup_datetime" not in df.columns:
        raise ValueError("Missing pickup datetime column (tpep_pickup_datetime)")

    # Load zone mapping for actual coordinates
    print("Loading NYC taxi zone coordinates...")
    zone_mapping = load_zone_mapping()
    
    df["pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["hour"] = df["pickup_datetime"].dt.hour

    # Map PULocationID to actual NYC coordinates
    def get_coordinates(location_id):
        return zone_mapping.get(location_id, (40.7128, -74.0060))  # Default to NYC center if not found
    
    df[['pickup_latitude', 'pickup_longitude']] = df['PULocationID'].apply(
        lambda x: pd.Series(get_coordinates(x))
    )

    # Create grid keys based on 0.01 degree grid cells (approximately 1km x 1km at this latitude)
    df["grid_x"] = (df["pickup_longitude"] * 100).apply(math.floor)
    df["grid_y"] = (df["pickup_latitude"] * 100).apply(math.floor)
    df["grid_key"] = df["grid_x"].astype(str) + "_" + df["grid_y"].astype(str)

    records = []
    for _, row in df.iterrows():
        rec = {
            "pickup_datetime": row["pickup_datetime"],
            "hour": int(row["hour"]),
            "trip_distance": float(row["trip_distance"]),
            "fare_amount": float(row["fare_amount"]),
            "pickup": {
                "type": "Point",
                "coordinates": [float(row["pickup_longitude"]), float(row["pickup_latitude"])]
            },
            "grid_x": int(row["grid_x"]),
            "grid_y": int(row["grid_y"]),
            "grid_key": row["grid_key"]
        }
        records.append(rec)

    if records:
        coll.insert_many(records)
        print(f"Inserted {len(records)} records into MongoDB.")
    else:
        print("No records inserted!")

    coll.create_index([("pickup_datetime", ASCENDING)])
    coll.create_index([("pickup", GEOSPHERE)])
    coll.create_index([("grid_key", ASCENDING)])
    print("Indexes created successfully.")
    return len(records)
