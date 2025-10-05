# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure VM                              │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Flask Web GUI (Port 5000)              │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Beautiful Web Interface              │  │    │
│  │  │  - Start/Stop buttons                        │  │    │
│  │  │  - Status indicator                          │  │    │
│  │  │  - Connection info display                   │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                        │                            │    │
│  │                        ▼                            │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         SITL Manager (Python)                │  │    │
│  │  │  - Process management                        │  │    │
│  │  │  - MAVLink configuration                     │  │    │
│  │  │  - Status monitoring                         │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────┐      ┌────────────────────────┐   │
│  │  MAVLink Router     │      │    PX4 SITL            │   │
│  │                     │      │                        │   │
│  │  UDP: 14550        │◄─────┤  X500 Quadcopter      │   │
│  │  TCP: 5760         │      │  Gazebo (headless)     │   │
│  │                     │      │                        │   │
│  └─────────┬───────────┘      └────────────────────────┘   │
│            │                                                │
└────────────┼────────────────────────────────────────────────┘
             │
             │ TCP Port 5760
             │
             ▼
    ┌────────────────────┐
    │  QGroundControl    │
    │  (Your Computer)   │
    └────────────────────┘
```

## Data Flow

### 1. Starting SITL

```
User clicks "Start SITL"
    │
    ▼
Flask API receives request
    │
    ▼
SITL Manager:
    1. Cleanup old processes
    2. Start MAVLink Router (UDP 14550 → TCP 5760)
    3. Start PX4 SITL (X500, headless Gazebo)
    4. Configure PX4 MAVLink (send to 0.0.0.0:14550)
    │
    ▼
Status updates to "Running"
    │
    ▼
Web interface displays connection info
```

### 2. Telemetry Flow

```
PX4 SITL
    │
    │ MAVLink messages
    │ UDP 14550
    ▼
MAVLink Router
    │
    │ Forward messages
    │ TCP 5760
    ▼
QGroundControl
```

## Components

### Flask Web App (`app.py`)
- **Purpose**: Web interface and API
- **Port**: 5000
- **Endpoints**:
  - `GET /` - Web interface
  - `GET /api/status` - Get SITL status
  - `POST /api/start` - Start SITL
  - `POST /api/stop` - Stop SITL

### SITL Manager (`sitl_manager.py`)
- **Purpose**: Manage PX4 and MAVLink router
- **Functions**:
  - `start()` - Start complete system
  - `stop()` - Stop all processes
  - `get_status()` - Get current status
  - `cleanup()` - Kill old processes
  - `configure_mavlink()` - Setup PX4 MAVLink

### MAVLink Router
- **Purpose**: Forward MAVLink messages
- **Input**: UDP 14550 (from PX4)
- **Output**: TCP 5760 (to QGC)
- **Command**: `mavlink-routerd 0.0.0.0:14550 -t 5760 -v`

### PX4 SITL
- **Purpose**: Simulate X500 quadcopter
- **Simulator**: Gazebo (headless)
- **Command**: `HEADLESS=1 make px4_sitl gz_x500`
- **MAVLink**: Configured to send to 0.0.0.0:14550

## Port Usage

| Port  | Protocol | Purpose                    |
|-------|----------|----------------------------|
| 5000  | TCP      | Web interface              |
| 5760  | TCP      | QGC connection             |
| 14550 | UDP      | PX4 → MAVLink Router       |

## Process Tree

```
python3 app.py (Flask)
    │
    ├─► mavlink-routerd (MAVLink Router)
    │
    └─► make px4_sitl gz_x500 (PX4 SITL)
            │
            ├─► cmake (Build system)
            │
            └─► px4 binary (Actual simulator)
                    │
                    └─► gz (Gazebo simulator)
```

## File Structure

```
CLOUDSITLSIM/
│
├── app.py                  # Flask web application
│   └── Routes: /, /api/status, /api/start, /api/stop
│
├── sitl_manager.py         # SITL management
│   └── Class: SITLManager
│       ├── start()
│       ├── stop()
│       ├── cleanup()
│       └── configure_mavlink()
│
├── templates/
│   └── index.html          # Web interface
│       ├── Status display
│       ├── Start/Stop buttons
│       └── Connection info
│
└── start.sh                # Startup script
```

## Security Considerations

### Azure VM Firewall Rules Needed:
- **Port 5000**: Web interface (TCP)
- **Port 5760**: QGC connection (TCP)

### Network Security Groups:
```
Inbound Rules:
- Port 5000: Allow from your IP (web interface)
- Port 5760: Allow from anywhere (QGC connections)
```

## Monitoring

### Check if running:
```bash
ps aux | grep "python3 app.py"    # Web app
ps aux | grep mavlink-routerd      # MAVLink router
ps aux | grep px4                  # PX4 SITL
```

### Check ports:
```bash
netstat -tlnp | grep 5000          # Web interface
netstat -tlnp | grep 5760          # QGC connection
netstat -ulnp | grep 14550         # MAVLink UDP
```

### Check logs:
```bash
# Web app logs are in terminal where start.sh was run
# MAVLink router: stdout/stderr captured by Python
# PX4 SITL: stdout/stderr captured by Python
```

## Scalability

This is designed for:
- ✅ Single SITL instance
- ✅ Multiple QGC connections (via MAVLink router)
- ✅ Simple deployment
- ✅ Easy maintenance

For multiple SITL instances, you would need:
- Different ports for each instance
- Multiple MAVLink routers
- Instance management system
