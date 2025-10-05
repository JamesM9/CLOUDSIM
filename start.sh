#!/bin/bash
# PX4 SITL Multi-Instance Web GUI

echo "============================================================"
echo "PX4 SITL Multi-Instance Web GUI - Starting"
echo "============================================================"

# Change to script directory
cd "$(dirname "$0")"

# Check if PX4-Autopilot exists
if [ ! -d "$HOME/PX4-Autopilot" ]; then
    echo "❌ Error: PX4-Autopilot not found at $HOME/PX4-Autopilot"
    echo "Please install PX4-Autopilot first"
    exit 1
fi

# Check if MAVLink router is installed
if ! command -v mavlink-routerd &> /dev/null; then
    echo "❌ Error: mavlink-routerd not installed"
    echo "Please install MAVLink router first"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -9 -f "python3 app.py" 2>/dev/null || true
pkill -9 -f "python3 app_multi.py" 2>/dev/null || true
pkill -9 mavlink-routerd 2>/dev/null || true
pkill -9 -f "px4.*sitl" 2>/dev/null || true

sleep 2

# Start the multi-instance web application
echo ""
echo "=================================================="
echo "🚀 Starting Multi-Instance Web GUI"
echo "=================================================="
echo ""
echo "Features:"
echo "• Create multiple SITL instances with different airframes"
echo "• Table view showing all instances and their status"
echo "• Individual control of each instance"
echo "• Automatic port management"
echo ""
echo "Web Interface: http://localhost:5000"
echo "Or: http://<your-vm-ip>:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app_multi.py
