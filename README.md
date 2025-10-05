# PX4 SITL Multi-Instance Web GUI

Powerful web interface to manage multiple PX4 SITL instances with different airframes simultaneously.

## Features

- ✅ **Table-based interface** showing all instances
- ✅ **Multiple instances** with different airframes
- ✅ **Individual control** - start/stop/remove each instance
- ✅ **Automatic port management** - no conflicts
- ✅ **Real-time status updates** every 3 seconds
- ✅ **QGroundControl connection info** for each instance
- ✅ **Bulk operations** - stop all instances at once
- ✅ **Clean, modern UI** with responsive design

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

4. **Create and start instances:**
   - Select an airframe from the dropdown
   - Click "Create Instance"
   - Click "Start" on the instance
   - Wait ~30 seconds for initialization

5. **Connect QGroundControl:**
   - Open QGroundControl
   - Settings → Comm Links → Add
   - Type: TCP
   - Host: `<IP shown in table>`
   - Port: `<TCP port shown for that instance>`
   - Click Connect

## How It Works

1. **MAVLink Router** starts on UDP port 14550 and forwards to TCP port 5760
2. **PX4 SITL** starts with X500 quadcopter model (headless Gazebo)
3. **PX4 MAVLink** is configured to send telemetry to the router
4. **QGroundControl** connects via TCP to the router

## File Structure

```
CLOUDSITLSIM/
├── app_multi.py           # Multi-instance Flask web application
├── multi_sitl_manager.py  # Multi-instance SITL management logic
├── templates/
│   └── index_multi.html   # Multi-instance web interface with table
├── requirements.txt       # Python dependencies
├── start.sh              # Start script (uses multi-instance)
└── README.md             # This file
```

## Troubleshooting

### Port 5000 already in use
```bash
pkill -9 -f "python3 app_multi.py"
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

- Click "Stop" on individual instances in the table
- Or click "Stop All Instances" for bulk stop
- Or press Ctrl+C in the terminal
- Or run: `pkill -9 -f "python3 app_multi.py"`

## Technical Details

- **Automatic Port Allocation**: Each instance gets unique ports
- **UDP Ports**: 14550, 14560, 14570, etc. (PX4 → MAVLink Router)
- **TCP Ports**: 5760, 5770, 5780, etc. (MAVLink Router → QGroundControl)
- **Web Port 5000**: Flask web interface
- **Supported Aircraft**: X500, VTOL, Planes, Rovers, etc.
- **Simulator**: Gazebo (headless mode)

## License

MIT License
# CLOUDSIM
# CLOUDSIM
