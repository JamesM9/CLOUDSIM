# 🚀 Quick Start Guide

## What You Have

A **simple, clean web interface** to run PX4 SITL (X500 quadcopter) with MAVLink router for QGroundControl connections on your Azure VM.

## Files Created

```
CLOUDSITLSIM/
├── app.py                    # Flask web application
├── sitl_manager.py           # SITL management logic
├── templates/
│   └── index.html            # Beautiful web interface
├── requirements.txt          # Python dependencies
├── start.sh                  # Start script
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

1. **Click "Start SITL"** - Wait ~30 seconds
2. **Note the IP address** displayed
3. **Open QGroundControl**
4. **Add TCP connection:**
   - Host: `<IP from web interface>`
   - Port: `5760`
5. **Click Connect**

## That's It!

The web interface is:
- ✅ Simple and clean
- ✅ Shows connection status
- ✅ Displays public IP automatically
- ✅ One-click start/stop
- ✅ Beautiful modern design

## Troubleshooting

**Web interface won't load:**
```bash
# Check if running
ps aux | grep "python3 app.py"

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
- Click "Stop SITL" button

**From terminal:**
```bash
pkill -9 -f "python3 app.py"
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

- ✅ Web interface loads
- ✅ Can click "Start SITL"
- ✅ Status changes to "Running"
- ✅ Public IP is displayed
- ✅ QGC connects successfully
- ✅ Can see vehicle in QGC

---

**That's it! Simple, clean, and it works.** 🎉
