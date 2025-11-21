#!/bin/bash

# Exit on error
set -e

# Parse command line arguments
APP_RUN=""
TEAM_NAME=""
RUN_SECONDS=""
DEBUG="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --app-run)
            APP_RUN="$2"
            shift 2
            ;;
        --team-name)
            TEAM_NAME="$2"
            shift 2
            ;;
        --run-seconds)
            RUN_SECONDS="$2"
            shift 2
            ;;
        --debug)
            DEBUG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --app-run [true|false] --team-name <team_name> [--run-seconds <seconds>] [--debug true|false]"
            exit 1
            ;;
    esac
done

# Validate app-run parameter
if [[ "$APP_RUN" != "true" && "$APP_RUN" != "false" ]]; then
    echo "Error: --app-run parameter is required and must be either 'true' or 'false'"
    exit 1
fi

# Validate team-name parameter
if [[ -z "$TEAM_NAME" ]]; then
    echo "Error: --team-name parameter is required"
    exit 1
fi

# If app-run is true, --run-seconds must be provided
if [[ "$APP_RUN" == "true" && -z "$RUN_SECONDS" ]]; then
    echo "Error: --run-seconds parameter is required when --app-run is true"
    exit 1
fi

# If app-run is false, set baseline runtime = 1 hour (3600 seconds)
if [[ "$APP_RUN" == "false" ]]; then
    RUN_SECONDS=3600
    echo "Baseline mode active: Running for 1 hour (3600 seconds)"
fi

# Validate debug parameter
if [[ "$DEBUG" != "true" && "$DEBUG" != "false" ]]; then
    DEBUG="false"
fi

echo "✓ Configuration: app_run=$APP_RUN, team_name=$TEAM_NAME, run_seconds=$RUN_SECONDS, debug=$DEBUG"
echo ""
echo "Checking system requirements..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "✗ Error: Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 found ($(python3 --version | awk '{print $2}'))"

# Check for pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "✗ Error: pip is not installed"
    exit 1
fi
echo "✓ pip found"

# Check for venv
if ! python3 -c "import venv" &> /dev/null; then
    echo "✗ Error: Python venv module is not available"
    exit 1
fi
echo "✓ Python venv available"

# Check for timeout
if ! command -v timeout &> /dev/null; then
    echo "✗ Error: timeout command not available"
    exit 1
fi
echo "✓ timeout command available"

echo "✓ All prerequisites satisfied"
echo ""

echo "[1/6] Creating Python virtual environment..."
python3 -m venv venv > /dev/null 2>&1
echo "✓ Virtual environment created"

echo "[2/6] Activating environment..."
source venv/bin/activate
echo "✓ Environment activated"

echo "[3/6] Installing required monitoring tools..."
pip install codecarbon > /dev/null 2>&1
echo "✓ Dependencies installed"

echo "[4/6] Generating configuration file..."
cat > .codecarbon.config << 'EOF'
[codecarbon]
offline = True
save_to_file = True
output_dir = ./emissions_logs
country_iso_code = IND
measure_power_secs = 15
tracking_mode = process
log_level = info
EOF
echo "✓ Configuration file created"

echo "[5/6] Preparing output folder..."
mkdir -p ./emissions_logs
echo "✓ Output folder ready"

echo "[6/6] Starting monitoring process for $RUN_SECONDS seconds..."
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "✗ Interrupted! Cleaning up..."
    if [[ -n "${MONITOR_PID:-}" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then
        kill "$MONITOR_PID" 2>/dev/null || true
        wait "$MONITOR_PID" 2>/dev/null || true
    fi
    pkill -f "codecarbon monitor" 2>/dev/null || true
    echo "✓ Cleanup completed"
    exit 130
}

trap cleanup SIGINT SIGTERM

timeout "${RUN_SECONDS}s" codecarbon monitor --offline --country-iso-code IND > /dev/null 2>&1 &
MONITOR_PID=$!

# Simple progress indicator
ELAPSED=0
while [[ $ELAPSED -lt $RUN_SECONDS ]]; do
    if ! kill -0 $MONITOR_PID 2>/dev/null; then
        break
    fi
    ELAPSED=$((ELAPSED + 1))
    PERCENT=$((ELAPSED * 100 / RUN_SECONDS))
    FILLED=$((PERCENT / 2))
    EMPTY=$((50 - FILLED))
    BAR=$(printf '%*s' "$FILLED" | tr ' ' '█')
    SPACES=$(printf '%*s' "$EMPTY" | tr ' ' '░')
    printf "\r  Progress: [%s%s] %3d%% | %ds remaining" "$BAR" "$SPACES" "$PERCENT" "$((RUN_SECONDS - ELAPSED))"
    sleep 1
done

echo ""
echo "✓ Monitoring completed successfully"

# Post-processing output
CSV_FILE=$(find ./emissions_logs -name "emissions*.csv" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
if [[ -z "$CSV_FILE" ]]; then
    echo "✗ Error: No output data file found"
    exit 1
fi

# Add metadata columns
sed -i '1s/$/,team_name/' "$CSV_FILE"
sed -i "2,\$s/\$/,$TEAM_NAME/" "$CSV_FILE"

sed -i '1s/$/,app_run/' "$CSV_FILE"
sed -i "2,\$s/\$/,$APP_RUN/" "$CSV_FILE"

echo "✓ Metadata added to output file"

# Rename output file
NEW_FILENAME="./emissions_logs/monitoring_app_run_${APP_RUN}.csv"
mv "$CSV_FILE" "$NEW_FILENAME"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✓ Process completed successfully!"
echo "════════════════════════════════════════════════════════════"
echo "  Output file: $NEW_FILENAME"
echo "  Team Name: $TEAM_NAME"
echo "  App Running: $APP_RUN"
echo "  Duration: $RUN_SECONDS seconds"
echo "════════════════════════════════════════════════════════════"
