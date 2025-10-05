# PX4 SITL Web GUI - X500 Quadcopter

Simple web interface to run PX4 SITL (X500 quadcopter) with MAVLink router for QGroundControl connections.

## Features

- ✅ Simple web interface
- ✅ One-click start/stop
- ✅ X500 quadcopter simulation
- ✅ MAVLink router for QGC connections
- ✅ Automatic public IP detection
- ✅ Clean, modern UI

## Prerequisites

1. **PX4-Autopilot** installed at `~/PX4-Autopilot`
2. **MAVLink Router** installed (`mavlink-routerd`)
3. **Python 3** with pip

## Quick Start

1. **Make the start script executable:**
   ```bash
   chmod +x start.sh
   ```

2. **Start the web GUI:**
   ```bash
   ./start.sh
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```
   Or from another computer:
   ```
   http://<your-vm-ip>:5000
   ```

4. **Click "Start SITL"** and wait ~30 seconds

5. **Connect QGroundControl:**
   - Open QGroundControl
   - Settings → Comm Links → Add
   - Type: TCP
   - Host: `<IP shown in web interface>`
   - Port: `5760`
   - Click Connect

## How It Works

1. **MAVLink Router** starts on UDP port 14550 and forwards to TCP port 5760
2. **PX4 SITL** starts with X500 quadcopter model (headless Gazebo)
3. **PX4 MAVLink** is configured to send telemetry to the router
4. **QGroundControl** connects via TCP to the router

## File Structure

```
CLOUDSITLSIM/
├── app.py              # Flask web application
├── sitl_manager.py     # SITL management logic
├── templates/
│   └── index.html      # Web interface
├── requirements.txt    # Python dependencies
├── start.sh           # Start script
└── README.md          # This file
```

## Troubleshooting

### Port 5000 already in use
```bash
pkill -9 -f "python3 app.py"
```

### SITL won't start
```bash
# Check if PX4 is built
ls ~/PX4-Autopilot/build/px4_sitl_default/bin/px4

# If not, build it
cd ~/PX4-Autopilot
make px4_sitl
```

### MAVLink router not found
```bash
# Check if installed
which mavlink-routerd

# If not, install it
# (Follow MAVLink router installation instructions)
```

### QGroundControl can't connect
- Make sure SITL is fully started (wait 30 seconds)
- Check firewall allows TCP port 5760
- Verify you're using the correct IP address
- Try connecting to `0.0.0.0:5760` if on same machine

## Stopping

- Click "Stop SITL" in the web interface
- Or press Ctrl+C in the terminal
- Or run: `pkill -9 -f "python3 app.py"`

## Technical Details

- **UDP Port 14550**: PX4 MAVLink → MAVLink Router
- **TCP Port 5760**: MAVLink Router → QGroundControl
- **Web Port 5000**: Flask web interface
- **Aircraft**: X500 Quadcopter
- **Simulator**: Gazebo (headless mode)

## License

MIT License
# CLOUDSIM
# CLOUDSIM
