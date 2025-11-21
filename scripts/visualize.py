# import folium, json

# def visualize(agg_file, html_out):
#     with open(agg_file) as f:
#         data = json.load(f)
#     m = folium.Map(location=[40.73, -73.93], zoom_start=11)
#     for d in data:
#         folium.CircleMarker(
#             location=[d["grid_y"]/100, d["grid_x"]/100],
#             radius=max(3, min(10, d["count"]/10)),
#             color="red" if d["count"] > 100 else "blue",
#             fill=True
#         ).add_to(m)
#     m.save(html_out)
#     print(f"Saved visualization → {html_out}")
import folium
import json
import statistics

def visualize(agg_file, html_out):
    with open(agg_file) as f:
        data = json.load(f)

    if not data:
        print("⚠️ No data to visualize.")
        return

    # --- NYC bounding box and your grid resolution ---
    MIN_LAT, MAX_LAT = 40.4774, 40.9176
    MIN_LON, MAX_LON = -74.2591, -73.7004
    GRID_SIZE = 0.01  # should match how you generated grid_x, grid_y

    # --- Compute approximate map center ---
    lats = [MIN_LAT + d["grid_y"] * GRID_SIZE for d in data]
    lons = [MIN_LON + d["grid_x"] * GRID_SIZE for d in data]
    center_lat = statistics.mean(lats)
    center_lon = statistics.mean(lons)

    # --- Create map ---
    m = folium.Map(location=[center_lat, center_lon],
                   zoom_start=11,
                   tiles="cartodbpositron")

    # --- Determine scaling range ---
    counts = [d["count"] for d in data]
    min_c, max_c = min(counts), max(counts)
    for d in data:
        # Convert grid_x, grid_y back to lat/lon
        lat = d["grid_y"] / 100 + 40
        lon = d["grid_x"] / 100 - 74

        folium.CircleMarker(
            location=[lat, lon],
            radius=max(3, min(10, d["count"] / 10)),
            color="red" if d["count"] > 100 else "blue",
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

    # # --- Add red circle markers ---
    # for d in data:
    #     lat = MIN_LAT + d["grid_y"] * GRID_SIZE
    #     lon = MIN_LON + d["grid_x"] * GRID_SIZE
    #     count = d["count"]

    #     # scale radius based on count, normalized
    #     radius = 5 + 10 * ((count - min_c) / (max_c - min_c + 1e-6))

    #     folium.CircleMarker(
    #         location=[lat, lon],
    #         radius=radius,
    #         color="#ff0000",         # 🔴 pure red outline
    #         fill=True,
    #         fill_color="#ff1a1a",    # bright red fill
    #         fill_opacity=0.8,        # make visible but not opaque
    #         weight=1,
    #         tooltip=f"<b>Grid:</b> {d['grid_key']}<br><b>Hour:</b> {d['hour']}<br><b>Count:</b> {count}"
    #     ).add_to(m)

    m.save(html_out)
    print(f"✅ Saved improved red hotspot visualization → {html_out}")

