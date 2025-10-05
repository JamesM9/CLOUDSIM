# 🚀 Quick Start Guide

## What You Have

A **powerful multi-instance web interface** to manage multiple PX4 SITL instances with different airframes simultaneously.

## Files Created

```
CLOUDSITLSIM/
├── app_multi.py              # Multi-instance Flask web application
├── multi_sitl_manager.py     # Multi-instance SITL management logic
├── templates/
│   └── index_multi.html      # Multi-instance web interface with table
├── requirements.txt          # Python dependencies
├── start.sh                  # Start script (uses multi-instance)
├── test_setup.sh             # Setup verification
├── px4-sitl-web.service      # Systemd service (optional)
├── README.md                 # Full documentation
├── SETUP.md                  # Detailed setup guide
└── QUICKSTART.md             # This file
```

## Prerequisites Check

Run this first:
```bash
cd ~/CLOUDSITLSIM
chmod +x test_setup.sh
./test_setup.sh
```

## If Prerequisites Missing

### Install PX4-Autopilot
```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
make px4_sitl
```

### Install MAVLink Router
```bash
cd ~
git clone https://github.com/mavlink-router/mavlink-router.git
cd mavlink-router
git submodule update --init --recursive
sudo apt install -y git ninja-build pkg-config gcc g++ systemd
meson setup build .
ninja -C build
sudo ninja -C build install
```

## Start the Application

```bash
cd ~/CLOUDSITLSIM
chmod +x start.sh
./start.sh
```

## Access the Web Interface

**From the VM:**
```
http://localhost:5000
```

**From your computer:**
```
http://<your-vm-public-ip>:5000
```

## Using the Web Interface

1. **Create instances:**
   - Select airframe from dropdown
   - Click "Create Instance"
   - Repeat for multiple instances
2. **Start instances:**
   - Click "Start" button for each instance
   - Wait ~30 seconds for initialization
3. **Note connection info** in the table
4. **Open QGroundControl**
5. **Add TCP connections:**
   - Host: `<IP from table>`
   - Port: `<TCP port for that instance>`
6. **Click Connect**

## That's It!

The web interface features:
- ✅ **Table view** showing all instances
- ✅ **Multiple airframes** (X500, VTOL, Planes, Rovers)
- ✅ **Individual control** of each instance
- ✅ **Real-time status updates**
- ✅ **Automatic port management**
- ✅ **Connection info** for each instance
- ✅ **Bulk operations** (stop all)

## Troubleshooting

**Web interface won't load:**
```bash
# Check if running
ps aux | grep "python3 app_multi.py"

# Check port
curl http://localhost:5000
```

**SITL won't start:**
```bash
# Check PX4 is built
ls ~/PX4-Autopilot/build/px4_sitl_default/bin/px4

# Check MAVLink router
which mavlink-routerd
```

**QGC won't connect:**
```bash
# Check processes
ps aux | grep mavlink
ps aux | grep px4

# Check ports
netstat -tlnp | grep 5760
```

## Stop the Application

**From web interface:**
- Click "Stop" on individual instances
- Or click "Stop All Instances"

**From terminal:**
```bash
pkill -9 -f "python3 app_multi.py"
```

## Auto-Start on Boot (Optional)

```bash
sudo cp px4-sitl-web.service /etc/systemd/system/
sudo systemctl enable px4-sitl-web
sudo systemctl start px4-sitl-web
```

## Support

- Full docs: `README.md`
- Setup guide: `SETUP.md`
- Test setup: `./test_setup.sh`

## Success Checklist

- ✅ Web interface loads with table
- ✅ Can create instances with different airframes
- ✅ Can start/stop individual instances
- ✅ Status updates in real-time
- ✅ Connection info displayed for each instance
- ✅ QGC connects successfully to instances
- ✅ Can see vehicles in QGC

---

**That's it! Simple, clean, and it works.** 🎉
