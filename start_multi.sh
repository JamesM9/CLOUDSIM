#!/bin/bash
"""
Start Multi-Instance PX4 SITL Web GUI
"""

echo "============================================================"
echo "Starting PX4 SITL Multi-Instance Web GUI"
echo "============================================================"

# Check if PX4-Autopilot exists
if [ ! -d "$HOME/PX4-Autopilot" ]; then
    echo "❌ PX4-Autopilot not found at $HOME/PX4-Autopilot"
    echo "Please install PX4-Autopilot first"
    exit 1
fi

# Check if mavlink-routerd is available
if ! command -v mavlink-routerd &> /dev/null; then
    echo "❌ mavlink-routerd not found"
    echo "Please install mavlink-router first"
    exit 1
fi

# Check if required Python packages are installed
echo "Checking Python dependencies..."
python3 -c "import flask, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing Python dependencies"
    echo "Please install requirements: pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ All dependencies found"
echo ""
echo "Starting multi-instance web interface..."
echo "Web interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Start the multi-instance Flask app
python3 app_multi.py
