# PX4 SITL Multi-Instance Manager

A powerful web-based interface for managing multiple PX4 SITL instances with different airframes simultaneously.

## Features

- **Multiple Instances**: Run multiple SITL instances with different airframes
- **Port Management**: Automatic port allocation to prevent conflicts
- **Individual Control**: Start, stop, and remove individual instances
- **Real-time Status**: Live status updates for all instances
- **Connection Info**: Per-instance QGroundControl connection details
- **Bulk Operations**: Stop all instances at once
- **Backward Compatibility**: Legacy single-instance API still works

## Supported Airframes

- **X500 Quadcopter** (default)
- **Standard VTOL**
- **RC Cessna Plane**
- **Advanced Plane**
- **Quad Tailsitter VTOL**
- **Tiltrotor VTOL**
- **Differential Rover**
- **Ackermann Rover**
- **Mecanum Rover**

## Port Allocation

Each instance gets unique ports to prevent conflicts:

| Instance | UDP Port | TCP Port | QGC Connection |
|----------|----------|----------|----------------|
| 1        | 14550    | 5760     | `<ip>:5760`    |
| 2        | 14560    | 5770     | `<ip>:5770`    |
| 3        | 14570    | 5780     | `<ip>:5780`    |
| 4        | 14580    | 5790     | `<ip>:5790`    |
| 5        | 14590    | 5800     | `<ip>:5800`    |
| ...      | ...      | ...      | ...            |
| 10       | 14640    | 5850     | `<ip>:5850`    |

## Quick Start

### 1. Start the Multi-Instance Web Interface

```bash
./start_multi.sh
```

### 2. Open Web Interface

Navigate to: `http://localhost:5000`

### 3. Create Instances

1. Select an airframe from the dropdown
2. Click "Add Instance"
3. Click "Start" on the instance to begin simulation
4. Wait ~30 seconds for full initialization

### 4. Connect QGroundControl

Each running instance shows its connection details:
- **IP Address**: Your VM's public IP
- **Port**: Unique TCP port for that instance
- **Protocol**: TCP

## API Endpoints

### Multi-Instance Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/instances` | Get all instances status |
| POST | `/api/instances` | Create new instance |
| GET | `/api/instances/{id}` | Get specific instance status |
| POST | `/api/instances/{id}/start` | Start specific instance |
| POST | `/api/instances/{id}/stop` | Stop specific instance |
| DELETE | `/api/instances/{id}` | Remove specific instance |
| POST | `/api/instances/stop-all` | Stop all instances |

### Legacy Endpoints (Backward Compatibility)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Get status (first instance or empty) |
| POST | `/api/start` | Create and start new instance |
| POST | `/api/stop` | Stop all instances |

## Usage Examples

### Create Multiple Instances

```bash
# Create X500 quadcopter
curl -X POST http://localhost:5000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"airframe": "gz_x500"}'

# Create Standard VTOL
curl -X POST http://localhost:5000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"airframe": "gz_standard_vtol"}'

# Create RC Cessna
curl -X POST http://localhost:5000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"airframe": "gz_rc_cessna"}'
```

### Start Specific Instance

```bash
curl -X POST http://localhost:5000/api/instances/instance_1/start
```

### Get All Instances Status

```bash
curl http://localhost:5000/api/instances
```

### Stop All Instances

```bash
curl -X POST http://localhost:5000/api/instances/stop-all
```

## Architecture

### Components

1. **MultiSITLManager**: Main manager for multiple instances
2. **SITLInstance**: Individual instance management
3. **PortPool**: Port allocation and conflict prevention
4. **Flask API**: RESTful API for web interface
5. **Web Interface**: Modern UI for instance management

### Process Management

Each instance runs independently:
- **PX4 SITL Process**: `make px4_sitl <airframe>`
- **MAVLink Router**: `mavlink-routerd <udp_port> -t <tcp_port>`
- **Gazebo Simulator**: Headless Gazebo for each airframe

### Resource Management

- **Memory**: ~200-300MB per instance
- **CPU**: 1-2 cores per instance
- **Network**: Unique ports per instance
- **Maximum**: 10 instances recommended

## File Structure

```
CLOUDSITLSIM/
├── app_multi.py              # Multi-instance Flask app
├── multi_sitl_manager.py    # Multi-instance management
├── templates/
│   └── index_multi.html     # Multi-instance web interface
├── start_multi.sh           # Multi-instance startup script
├── test_multi_instance.py   # Comprehensive tests
└── README_MULTI.md          # This file
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_multi_instance.py
```

This tests:
- Instance creation and management
- Port allocation and conflict prevention
- Flask API endpoints
- Cleanup and resource management

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Each instance gets unique ports automatically
2. **Resource Exhaustion**: Limit to 5-8 instances on typical VMs
3. **Process Cleanup**: Use "Stop All" to clean up all instances
4. **Gazebo Issues**: Ensure headless mode is working

### Monitoring

Check running processes:
```bash
ps aux | grep px4
ps aux | grep mavlink-routerd
ps aux | grep gz
```

Check port usage:
```bash
netstat -tlnp | grep 576
netstat -ulnp | grep 145
```

## Migration from Single Instance

The multi-instance system is backward compatible:

1. **Legacy API**: Old single-instance endpoints still work
2. **Same Interface**: Original web interface still available
3. **Gradual Migration**: Can run both systems simultaneously

## Performance Considerations

- **Startup Time**: ~30 seconds per instance
- **Memory Usage**: Monitor system resources
- **Network**: Each instance needs unique ports
- **CPU**: Gazebo simulation is CPU intensive

## Security

- **Firewall**: Open ports 5000 (web) and 5760-5850 (QGC)
- **Network**: Each instance isolated by unique ports
- **Process**: Individual process management per instance

## Future Enhancements

- **Instance Templates**: Save common configurations
- **Resource Monitoring**: CPU/Memory usage per instance
- **Auto-scaling**: Dynamic instance management
- **Load Balancing**: Distribute instances across VMs
