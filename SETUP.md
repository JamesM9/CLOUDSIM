# Setup Guide for Azure VM

## Step 1: Install PX4-Autopilot

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
make px4_sitl
```

## Step 2: Install MAVLink Router

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

## Step 3: Install Python Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

## Step 4: Setup CloudSITLSIM

```bash
cd ~/CLOUDSITLSIM
chmod +x start.sh
pip3 install -r requirements.txt
```

## Step 5: Configure Azure VM Firewall

Allow inbound traffic on:
- **Port 5000** (Web Interface)
- **Port 5760** (QGroundControl TCP)

In Azure Portal:
1. Go to your VM → Networking → Add inbound port rule
2. Add rule for port 5000 (TCP)
3. Add rule for port 5760 (TCP)

## Step 6: Start the Application

```bash
cd ~/CLOUDSITLSIM
./start.sh
```

## Step 7: Access the Web Interface

Open browser:
```
http://<your-vm-public-ip>:5000
```

## Step 8: Connect QGroundControl

1. Click "Start SITL" in web interface
2. Wait 30 seconds
3. Open QGroundControl
4. Settings → Comm Links → Add
5. Type: TCP
6. Host: `<your-vm-public-ip>`
7. Port: `5760`
8. Connect

## Quick Commands

**Start:**
```bash
cd ~/CLOUDSITLSIM && ./start.sh
```

**Stop:**
```bash
pkill -9 -f "python3 app.py"
```

**Check Status:**
```bash
ps aux | grep -E "(mavlink|px4|app.py)"
```

**View Logs:**
```bash
# Web app logs are in the terminal where you ran start.sh
```

## Troubleshooting

**Can't access web interface:**
- Check Azure firewall allows port 5000
- Try: `curl http://localhost:5000`

**QGC can't connect:**
- Check Azure firewall allows port 5760
- Verify SITL is running: `ps aux | grep px4`
- Check MAVLink router: `ps aux | grep mavlink`

**SITL fails to start:**
- Check PX4 is built: `ls ~/PX4-Autopilot/build/px4_sitl_default/bin/px4`
- Rebuild if needed: `cd ~/PX4-Autopilot && make px4_sitl`

## Success Indicators

When everything is working:
- ✅ Web interface shows "Running" status
- ✅ Public IP is displayed
- ✅ `ps aux | grep mavlink` shows mavlink-routerd process
- ✅ `ps aux | grep px4` shows px4 process
- ✅ QGC connects and shows vehicle data
