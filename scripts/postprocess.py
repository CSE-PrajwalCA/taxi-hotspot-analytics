import json
import numpy as np
import os

def detect_anomalies(input_file, out_file, threshold=3.0):
    """
    Detect anomalies based on z-score analysis per grid cell.
    
    For each grid cell, compares the trip count for each hour against
    the distribution of that grid cell across all 24 hours.
    
    Args:
        input_file: Path to aggregated hotspots JSON
        out_file: Path to save anomaly results
        threshold: Z-score threshold (default 3.0 = ~0.3% outliers)
    """
    with open(input_file) as f:
        data = json.load(f)

    # Group data by grid_key AND hour (preserve hour information)
    df = {}
    for row in data:
        k = row["grid_key"]
        hour = row.get("hour")
        count = row["count"]
        
        if k not in df:
            df[k] = {}
        df[k][hour] = count

    anomalies = []
    
    # For each grid cell, analyze all 24 hours
    for grid_key, hours_dict in df.items():
        # Get counts for all 24 hours (0 if hour not present)
        counts = [hours_dict.get(h, 0) for h in range(24)]
        
        mean = np.mean(counts)
        std = np.std(counts)
        
        # Check each hour for anomalies
        for hour in range(24):
            count = counts[hour]
            
            # Calculate z-score
            if std > 0:
                z_score = (count - mean) / std
                
                # Flag if z-score exceeds threshold
                if abs(z_score) > threshold:
                    anomalies.append({
                        "grid_key": grid_key,
                        "hour": hour,
                        "count": count,
                        "zscore": round(z_score, 2)
                    })
    
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(anomalies, f, indent=2)
    
    print(f"Anomaly detection complete: {len(anomalies)} anomalies → {out_file}")
    return anomalies
