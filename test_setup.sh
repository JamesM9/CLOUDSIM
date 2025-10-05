#!/bin/bash
# Test script to verify setup

echo "=================================================="
echo "PX4 SITL Setup Verification"
echo "=================================================="

# Test 1: Check PX4-Autopilot
echo ""
echo "1. Checking PX4-Autopilot..."
if [ -d "$HOME/PX4-Autopilot" ]; then
    echo "   ✅ PX4-Autopilot directory found"
    if [ -f "$HOME/PX4-Autopilot/build/px4_sitl_default/bin/px4" ]; then
        echo "   ✅ PX4 binary found (built)"
    else
        echo "   ⚠️  PX4 not built - run: cd ~/PX4-Autopilot && make px4_sitl"
    fi
else
    echo "   ❌ PX4-Autopilot not found at $HOME/PX4-Autopilot"
fi

# Test 2: Check MAVLink Router
echo ""
echo "2. Checking MAVLink Router..."
if command -v mavlink-routerd &> /dev/null; then
    echo "   ✅ mavlink-routerd found: $(which mavlink-routerd)"
else
    echo "   ❌ mavlink-routerd not found"
fi

# Test 3: Check Python
echo ""
echo "3. Checking Python..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 found: $(python3 --version)"
else
    echo "   ❌ Python3 not found"
fi

# Test 4: Check Python packages
echo ""
echo "4. Checking Python packages..."
if python3 -c "import flask" 2>/dev/null; then
    echo "   ✅ Flask installed"
else
    echo "   ⚠️  Flask not installed - run: pip3 install -r requirements.txt"
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ Requests installed"
else
    echo "   ⚠️  Requests not installed - run: pip3 install -r requirements.txt"
fi

# Test 5: Check files
echo ""
echo "5. Checking files..."
files=("app.py" "sitl_manager.py" "templates/index.html" "requirements.txt" "start.sh")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
    fi
done

# Test 6: Check ports
echo ""
echo "6. Checking ports..."
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ⚠️  Port 5000 already in use"
else
    echo "   ✅ Port 5000 available"
fi

if lsof -Pi :5760 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ⚠️  Port 5760 already in use"
else
    echo "   ✅ Port 5760 available"
fi

# Summary
echo ""
echo "=================================================="
echo "Setup Verification Complete"
echo "=================================================="
echo ""
echo "If all checks passed, run: ./start.sh"
echo ""
