# 🚕 Taxi Hotspot Analytics

A comprehensive data analytics platform for identifying and visualizing taxi pickup hotspots in New York City using NYC Yellow Taxi Trip data from January 2019. This project demonstrates large-scale data processing with MongoDB, comparing aggregation pipeline and MapReduce approaches, while also tracking carbon emissions throughout execution.

---

## 📋 Project Overview

This project analyzes taxi trip patterns to identify geographic hotspots (high-demand pickup locations) and temporal variations (busiest hours). It implements two parallel data processing approaches:

1. **MongoDB Aggregation Pipeline** - Native MongoDB aggregation framework for efficient data grouping
2. **MongoDB MapReduce** - Classic MapReduce paradigm for distributed-like processing

The system compares both approaches in terms of accuracy, performance, and resource consumption, while providing an interactive web dashboard for visualization and anomaly detection.

---

## 🏗️ Project Structure

```
taxi-hotspot-analytics/
├── README.md                      # This file - comprehensive documentation
├── requirements.txt               # Python dependencies for the entire project
├── emission_calculation.sh        # Bash script for carbon emissions monitoring
├── .codecarbon.config            # CodeCarbon configuration for emissions tracking
├── .gitignore                    # Git ignore patterns
│
├── backend/                      # Flask web server and application logic
│   ├── app.py                    # **Unified main Flask application (PRIMARY)**
│   ├── app1.py                   # Alternative Flask app (legacy/backup)
│   ├── compare_app.py            # Comparison dashboard Flask app (legacy)
│   ├── requirements_backend.txt  # Backend-specific dependencies (currently empty)
│   ├── templates/                # Jinja2 templates served by Flask
│   │   └── index.html            # Main dashboard HTML template
│   ├── data/                     # Backend-specific data copies
│   │   └── results/              # Results data directory
│   │       ├── anomaly_cells.json
│   │       ├── hourly_grid_counts.json
│   │       └── mapreduce_hourly_grid_counts.json
│
├── frontend/                     # Web UI components
│   ├── index.html                # Interactive hotspot visualization dashboard
│   ├── compare.html              # Comparison dashboard (aggregation vs mapreduce)
│   ├── js/
│   │   └── app.js                # JavaScript for interactive map and controls
│   └── css/
│       └── styles.css            # CSS styling for web interface
│
├── scripts/                      # Core data processing modules
│   ├── ingest.py                 # Data ingestion from CSV to MongoDB
│   ├── aggregate.py              # MongoDB aggregation pipeline implementation
│   ├── mapreduce.py              # MongoDB MapReduce implementation
│   ├── postprocess.py            # Anomaly detection using statistical methods
│   ├── visualize.py              # Folium-based map visualization (legacy)
│   └── __pycache__/              # Python bytecode cache
│
├── data/                         # Data storage and results
│   ├── raw/
│   │   └── yellow_tripdata_2019-01.csv  # NYC Yellow Taxi raw data (January 2019)
│   └── results/                  # Processed results and outputs
│       ├── anomaly_cells.json           # Detected anomalies with z-scores
│       ├── hourly_grid_counts.json      # Aggregation pipeline results
│       ├── mapreduce_hourly_grid_counts.json # MapReduce results
│       ├── timing.json                  # Execution timing metrics
│       └── timing_history.json          # Historical timing records
│
├── docs/                         # Documentation
│   ├── report.md                 # Project report (currently empty)
│   └── visuals/                  # Visualization outputs and charts
│
├── emissions_logs/               # Carbon emissions tracking
│   └── monitoring_app_run_*.csv  # CodeCarbon emissions monitoring logs
│
└── venv/                         # Python virtual environment (if created)
```

---

## 📁 Detailed File Descriptions

### Root Level Files

#### `README.md`
The main documentation file you're reading. Provides comprehensive overview of the project structure, setup instructions, and file descriptions.

#### `requirements.txt`
**Core project dependencies:**
```
pandas        - Data manipulation and CSV reading
pymongo       - MongoDB Python driver
flask         - Web server and API framework
folium        - Interactive map visualization library
numpy         - Numerical computing for anomaly detection
```

#### `emission_calculation.sh`
**Bash script for monitoring carbon emissions during execution.**
- Validates system requirements (Python 3, pip, venv)
- Creates and activates a Python virtual environment
- Installs CodeCarbon monitoring tool
- Configures monitoring with `.codecarbon.config`
- Tracks process-level carbon emissions for specified duration
- Outputs results to `emissions_logs/`

**Usage:**
```bash
./emission_calculation.sh --app-run true --team-name "TeamName" --run-seconds 600 --debug false
./emission_calculation.sh --app-run false --team-name "TeamName"  # Baseline: 1 hour
```

#### `.codecarbon.config`
**CodeCarbon configuration file for emissions tracking:**
- `offline = True` - Uses standard CPU model for baseline emissions
- `country_iso_code = IND` - Uses India electricity grid for emissions calculation
- `output_dir = ./emissions_logs` - Saves monitoring data locally
- `tracking_mode = process` - Tracks individual process emissions

#### `.gitignore`
Currently empty, can be configured to exclude large data files and venv.

---

### Backend Directory (`backend/`)

#### `app.py` ⭐ **PRIMARY APPLICATION**
**Unified Flask web server implementing the complete taxi hotspot analytics pipeline.**

**Key Features:**
- **Full pipeline execution**: Ingests CSV → Aggregates → MapReduce → Detects anomalies
- **REST API endpoints**:
  - `/` - Serves main dashboard (index.html)
  - `/api/hotspots?hour=<0-23>` - Returns hotspots for specific hour
  - `/api/anomalies` - Returns detected anomalies with z-scores
  - `/compare` - Serves comparison dashboard
  - `/api/compare?hour=<int>` - Returns comparison metrics between aggregation and MapReduce
  - `/api/trend` - Returns historical timing trends

**Key Functions:**
- `run_full_pipeline()` - Orchestrates entire data processing workflow
- `ensure_results_dir()` - Creates output directory structure
- `load_json_safe()` - Safely loads JSON files with error handling
- `compare_results()` - Compares aggregation vs MapReduce results

**Configuration:**
```python
MONGO_URI = "mongodb://localhost:27017"  # MongoDB connection string
DB_NAME = "taxi_hotspot_db"              # Database name
CSV_PATH = "data/raw/yellow_tripdata_2019-01.csv"
```

**Execution Timing Tracked:**
- Ingestion time (CSV → MongoDB)
- Aggregation time
- MapReduce time
- Anomaly detection time

#### `app1.py`
**Alternative Flask application implementation** (legacy/backup)
- Similar functionality to `app.py` but with different routing structure
- Contains commented-out legacy code
- Serves the same frontend files
- Implemented as a fallback option

#### `compare_app.py`
**Standalone comparison dashboard Flask application** (legacy)
- Compares results from aggregation and MapReduce approaches
- Provides detailed accuracy metrics (MAE, RMSE, exact match percentage)
- Tracks performance differences and speed ratios
- Implements timing history logging

**Key Endpoints:**
- `/` - Renders comparison dashboard
- `/api/compare?hour=<int>` - Returns comparison metrics
- `/api/trend` - Returns historical timing data

#### `requirements_backend.txt`
**Backend-specific dependencies file** (currently empty)
- Can be used for environment-specific backend requirements
- Typically superseded by root `requirements.txt`

#### `templates/index.html`
**Jinja2 HTML template** served by Flask for the main dashboard.
- Defines the HTML structure for the interactive map
- Includes controls for hour selection
- Links to Leaflet library (CDN) for map rendering
- References frontend CSS and JavaScript files

---

### Frontend Directory (`frontend/`)

#### `index.html`
**Main interactive dashboard HTML file**
- **Title**: NYC Taxi Hotspots
- **Features**:
  - Interactive Leaflet map centered on NYC
  - Hour selector input (0-23)
  - Load Hotspots button
  - Responsive layout
- **External Libraries**:
  - Leaflet.js for map rendering (CDN)
  - OpenStreetMap tiles as base layer
- **Dynamic Content**: Populated by JavaScript (`app.js`)

#### `compare.html`
**Comparison dashboard between aggregation and MapReduce approaches**
- **Features**:
  - Execution summary metrics
  - Accuracy comparison (MAE, RMSE, exact match percentage)
  - Performance metrics and charts
  - Hour-based filtering
  - Refresh button for re-running comparisons
- **Libraries**: Bootstrap 5.3, Chart.js for visualization

#### `js/app.js`
**Frontend JavaScript for interactive map functionality**

**Key Functions:**
- `drawHotspots()` - Renders taxi hotspot circles on the map
  - Circle radius scales with trip count
  - Color coding: orange for hotspots
  - Popups show grid key, count, and average fare
- `drawAnomalies()` - Renders detected anomalies as red markers
  - Shows z-score for anomaly magnitude
- `loadHotspots()` - Fetches hotspot data from API for selected hour
- Event listeners for hour input and load button

**Map Configuration:**
- Center: New York City (40.73, -73.93)
- Zoom level: 11
- Base layer: OpenStreetMap

#### `css/styles.css`
**CSS styling for the web interface**
- Full-height responsive layout
- Header styling with white background
- Map container takes remaining height
- Clean, minimal design
- Font: Arial, sans-serif

---

### Scripts Directory (`scripts/`)

#### `ingest.py`
**Data ingestion module: Converts CSV to MongoDB documents**

**Key Function**: `ingest_data(csv_path, mongo_uri, db_name, sample_rows, drop)`

**Processing Steps:**
1. Reads CSV file (yellow taxi trip data)
2. Parses `tpep_pickup_datetime` column
3. Extracts hour from timestamp
4. **Grid mapping**: Converts `PULocationID` to pseudo-coordinates:
   - `pickup_latitude = PULocationID // 50 + 40.5`
   - `pickup_longitude = -74 + (PULocationID % 50) * 0.02`
5. Computes grid coordinates:
   - `grid_x = floor(pickup_longitude * 100)`
   - `grid_y = floor(pickup_latitude * 100)`
   - `grid_key = "grid_x_grid_y"` (unique grid cell identifier)

**Document Structure Inserted**:
```json
{
  "pickup_datetime": "2019-01-01 12:34:56",
  "hour": 12,
  "trip_distance": 2.5,
  "fare_amount": 12.50,
  "pickup": {
    "type": "Point",
    "coordinates": [-73.95, 40.67]
  },
  "grid_x": -7395,
  "grid_y": 4067,
  "grid_key": "-7395_4067"
}
```

**Indexes Created**:
- Ascending index on `pickup_datetime` (for time-range queries)
- GeoSpatial index on `pickup` (for geographic queries)
- Ascending index on `grid_key` (for grid-based aggregations)

**Parameters**:
- `sample_rows` - Number of rows to ingest (None = all)
- `drop` - Whether to drop existing collection before ingestion

#### `aggregate.py`
**MongoDB aggregation pipeline for grouping hotspot data**

**Aggregation Pipeline**:
```javascript
// Stage 1: Group by grid_cell and hour
$group: {
  _id: { grid_key, hour },
  count: sum of trips,
  avg_fare: average fare,
  avg_distance: average trip distance,
  grid_x, grid_y: first values
}

// Stage 2: Project fields
$project: {
  grid_key, hour, count, avg_fare, avg_distance, grid_x, grid_y
}
```

**Output**: `data/results/hourly_grid_counts.json`
- JSON array of aggregated results
- One document per (grid_key, hour) combination
- Includes count and statistical metrics

**Key Features**:
- Native MongoDB aggregation (typically faster)
- Memory-efficient for large datasets
- Directly queryable results

#### `mapreduce.py`
**MongoDB MapReduce implementation for comparison**

**Map Function**:
```javascript
emit({grid_key, hour}, {
  count: 1,
  fare_sum: this.fare_amount,
  dist_sum: this.trip_distance
})
```

**Reduce Function**:
```javascript
Sums all counts and distances for each (grid_key, hour) key
```

**Finalize Function**:
```javascript
Computes averages: avg_fare = fare_sum / count, avg_distance = dist_sum / count
```

**Output**: `data/results/mapreduce_hourly_grid_counts.json`

**Key Features**:
- Classic distributed processing pattern
- Results returned inline (not written to collection)
- Allows performance comparison with aggregation pipeline

#### `postprocess.py`
**Anomaly detection using statistical z-score analysis**

**Algorithm**:
1. Group counts by grid_key
2. For each grid_key, compute mean and standard deviation
3. For each count, calculate z-score: `(count - mean) / std`
4. Flag as anomaly if `|z-score| > threshold` (default: 3.0)

**Anomaly Document**:
```json
{
  "grid_key": "-7395_4067",
  "hour": 15,
  "count": 150,
  "zscore": 3.45
}
```

**Output**: `data/results/anomaly_cells.json`

**Use Case**: Identifies unusual traffic patterns (potential events, accidents, transit issues)

#### `visualize.py`
**Folium-based interactive map visualization** (legacy, mostly commented)

**Active Implementation**:
- Creates Folium map centered on computed data center
- Renders circle markers for each hotspot
- Circle radius proportional to trip count
- Color coding: Red if count > 100, else blue
- Includes statistics calculation and grid-to-latlon conversion

**Output**: HTML file with interactive Folium map

#### `__pycache__/`
**Python bytecode cache directory**
- Auto-generated by Python
- Contains compiled versions of imported modules
- Speeds up module loading on subsequent runs

---

### Data Directory (`data/`)

#### `raw/yellow_tripdata_2019-01.csv`
**Raw NYC Yellow Taxi trip data for January 2019**
- **Source**: NYC Taxi and Limousine Commission (TLC)
- **Format**: CSV with the following key columns:
  - `tpep_pickup_datetime` - Pickup timestamp
  - `tpep_dropoff_datetime` - Dropoff timestamp
  - `trip_distance` - Distance traveled
  - `fare_amount` - Base fare
  - `PULocationID` - Pickup location zone ID
  - `DOLocationID` - Dropoff location zone ID
  - Other: tips, tolls, total amount, payment type, etc.
- **Rows**: Thousands of records
- **Size**: Substantial CSV file (used with sampling for processing)

#### `results/hourly_grid_counts.json`
**Aggregation pipeline results**
- Array of objects with structure:
  ```json
  {
    "grid_key": "string",
    "hour": 0-23,
    "count": number of trips,
    "avg_fare": average fare amount,
    "avg_distance": average trip distance,
    "grid_x": grid x coordinate,
    "grid_y": grid y coordinate
  }
  ```
- Used for main hotspot visualization
- Updated each pipeline run

#### `results/mapreduce_hourly_grid_counts.json`
**MapReduce results with identical schema to aggregation output**
- Same structure as `hourly_grid_counts.json`
- Generated for comparison analysis
- Allows validation of MapReduce vs aggregation accuracy

#### `results/anomaly_cells.json`
**Detected anomalies with z-scores**
```json
[
  {
    "grid_key": "string",
    "hour": 0-23,
    "count": number,
    "zscore": float
  }
]
```
- Filtered list of unusual patterns
- Z-score indicates magnitude of anomaly
- Visualized as red markers on map

#### `results/timing.json`
**Execution timing metrics from latest pipeline run**
```json
{
  "ingest_time": 1.234,
  "aggregation_time": 0.567,
  "mapreduce_time": 2.890,
  "anomaly_time": 0.123
}
```
- All times in seconds
- Used for performance tracking

#### `results/timing_history.json`
**Historical timing data** (last 20 runs)
```json
[
  {
    "timestamp": "HH:MM:SS",
    "agg_time": 0.567,
    "mapr_time": 2.890
  }
]
```
- Used for trend analysis on comparison dashboard
- Circular buffer (keeps last 20 entries)

---

### Docs Directory (`docs/`)

#### `report.md`
**Project report file** (currently empty)
- Intended for detailed project analysis and findings
- Can include methodology, results, and conclusions
- Recommended for academic or technical documentation

#### `visuals/`
**Directory for visualization outputs**
- Can store generated maps, charts, and statistical plots
- Output location for `visualize.py` results
- Intended for documentation and presentation materials

---

### Emissions Logs Directory (`emissions_logs/`)

#### `monitoring_app_run_*.csv`
**CodeCarbon emissions monitoring data**
- Generated by `emission_calculation.sh`
- Tracks CPU power consumption over time
- Contains columns:
  - Timestamp
  - Power (watts)
  - Energy (Joules)
  - Carbon equivalent (grams CO2)
  - CPU utilization
- Multiple runs saved with different filenames (true/false for app_run)
- Used to assess environmental impact of data processing

---

## 🚀 Setup and Usage

### Prerequisites
- Python 3.7+
- MongoDB 4.0+ (running on localhost:27017 or configured via MONGO_URI)
- bash shell

### Installation

1. **Clone or navigate to project**:
```bash
cd /path/to/taxi-hotspot-analytics
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Ensure MongoDB is running**:
```bash
# Example: Start MongoDB locally
mongod --dbpath /path/to/data
```

### Running the Application

#### Option 1: Run Complete Pipeline with Flask Server
```bash
cd backend
python app.py
```
- Processes entire pipeline (ingest → aggregate → mapreduce → anomalies)
- Launches Flask server on `http://127.0.0.1:5000`
- Access dashboard at `http://127.0.0.1:5000`
- Comparison dashboard at `http://127.0.0.1:5000/compare`

#### Option 2: Run Individual Components (Python REPL)
```python
from scripts.ingest import ingest_data
from scripts.aggregate import run_aggregation
from scripts.mapreduce import run_mapreduce
from scripts.postprocess import detect_anomalies

# Ingest data
ingest_data("data/raw/yellow_tripdata_2019-01.csv", 
            "mongodb://localhost:27017", 
            "taxi_hotspot_db", 
            sample_rows=100000, 
            drop=True)

# Run aggregation
run_aggregation("mongodb://localhost:27017", 
                "taxi_hotspot_db", 
                "data/results/hourly_grid_counts.json")

# Run MapReduce
run_mapreduce("mongodb://localhost:27017", 
              "taxi_hotspot_db", 
              "data/results/mapreduce_hourly_grid_counts.json")

# Detect anomalies
detect_anomalies("data/results/hourly_grid_counts.json", 
                 "data/results/anomaly_cells.json")
```

#### Option 3: Monitor Emissions
```bash
./emission_calculation.sh --app-run true --team-name "MyTeam" --run-seconds 600
```

---

## 📊 API Reference

### Hotspot Endpoints

**GET `/api/hotspots`**
- Query Parameters: `hour` (optional, 0-23)
- Response: JSON array of hotspot objects
```json
[
  {
    "grid_key": "-7395_4067",
    "hour": 12,
    "count": 145,
    "avg_fare": 12.50,
    "avg_distance": 2.35,
    "grid_x": -7395,
    "grid_y": 4067
  }
]
```

**GET `/api/anomalies`**
- Query Parameters: None
- Response: JSON array of anomaly objects with z-scores

### Comparison Endpoints

**GET `/api/compare`**
- Query Parameters: `hour` (optional, 0-23)
- Response: Comprehensive comparison metrics
```json
{
  "total_rows_agg": 1234,
  "total_rows_mapr": 1234,
  "common_keys": 1200,
  "agg_only": 34,
  "mapr_only": 0,
  "exact_matches": 1200,
  "exact_pct": 100.0,
  "mae": 0.0,
  "rmse": 0.0,
  "aggregation_time": 0.567,
  "mapreduce_time": 2.890,
  "speed_ratio": 5.1,
  "trend": [...]
}
```

**GET `/api/trend`**
- Query Parameters: None
- Response: Historical timing data (last 10-20 records)

---

## 🔑 Key Concepts

### Grid-Based Spatial Analysis
- Divides NYC into a regular grid of cells
- Each cell identified by `grid_x_grid_y` key
- Aggregates trip counts by grid cell and hour
- Enables efficient hotspot identification

### Hotspot Definition
- Geographic areas with high concentration of taxi pickups
- Identified by grouping trips into grid cells
- Visualized as circles on interactive map
- Circle size proportional to trip count

### Anomaly Detection
- Uses z-score statistical method
- Identifies hours with unusual trip counts for each grid cell
- Threshold: 3.0 standard deviations from mean
- Indicates potential events or unusual traffic patterns

### Performance Comparison
- **Aggregation Pipeline**: MongoDB native method, typically faster
- **MapReduce**: Classic distributed approach, more flexible but slower
- Compared on accuracy (MAE, RMSE) and execution time
- Tests show aggregation ~5-6x faster than MapReduce

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Server | Flask | REST API and web server |
| Database | MongoDB | Storing and querying taxi trip data |
| Data Processing | Python (pandas, numpy) | ETL and data manipulation |
| Frontend Map | Leaflet.js | Interactive map visualization |
| Charting | Chart.js | Performance metrics visualization |
| Styling | Bootstrap 5 | Responsive UI components |
| Emissions Tracking | CodeCarbon | Carbon footprint monitoring |

---

## 📝 Notes

- **Data Sampling**: By default, pipeline uses 5,000 rows for speed; modify `sample_rows` parameter for full dataset
- **MongoDB Connection**: Set `MONGO_URI` environment variable to use non-standard MongoDB connection strings
- **Performance**: MapReduce significantly slower than aggregation pipeline on tested dataset
- **Grid Resolution**: Current grid resolution ~0.01 degrees (~1km); adjust multipliers in `ingest.py` for finer/coarser granularity
- **Anomaly Threshold**: Default z-score threshold of 3.0 identifies ~0.3% of data points; adjust in `postprocess.py` for sensitivity tuning

---

## 📄 License & Attribution

This project analyzes data from the NYC Taxi and Limousine Commission (TLC).
- Original data source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Project focus: Data engineering, aggregation techniques, and emissions tracking

---

## 👨‍💻 Development Notes

### File Dependencies
```
app.py
  ├── scripts/ingest.py
  ├── scripts/aggregate.py
  ├── scripts/mapreduce.py
  ├── scripts/postprocess.py
  ├── frontend/index.html
  └── frontend/compare.html

frontend/index.html
  ├── frontend/js/app.js
  └── frontend/css/styles.css

ingest.py
  └── data/raw/yellow_tripdata_2019-01.csv
```

### Common Issues & Solutions

**MongoDB Connection Error**
- Ensure MongoDB daemon is running: `mongod`
- Check connection string in `MONGO_URI`
- Verify port 27017 is accessible

**Missing Data File**
- Ensure `data/raw/yellow_tripdata_2019-01.csv` exists
- Run with `sample_rows=None` to process all available data
- Check file permissions

**Slow Performance**
- Reduce `sample_rows` parameter for faster testing
- Use aggregation over MapReduce for production
- Consider database indexing optimization

---

## 📞 Quick Reference

**Start Application**: `python backend/app.py`
**Dashboard URL**: `http://127.0.0.1:5000`
**Comparison Dashboard**: `http://127.0.0.1:5000/compare`
**API Base**: `http://127.0.0.1:5000/api/`
**MongoDB Required**: Yes
**Data File Required**: Yes
**Virtual Environment**: Recommended

---

## 🎯 Project Goals

✅ Identify NYC taxi pickup hotspots  
✅ Compare aggregation vs MapReduce performance  
✅ Detect anomalous traffic patterns  
✅ Provide interactive visualization dashboard  
✅ Track environmental impact of processing  
✅ Demonstrate data engineering best practices  

---

*Last Updated: November 2025*
*Project Type: Data Engineering & Analytics*
