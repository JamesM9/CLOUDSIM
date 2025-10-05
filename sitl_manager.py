#!/usr/bin/env python3
"""
Simple SITL Manager for X500 Quadcopter
Runs PX4 SITL and MAVLink router for QGroundControl connection
"""

import subprocess
import time
import os
import signal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SITLManager:
    def __init__(self):
        self.px4_path = os.path.expanduser("~/PX4-Autopilot")
        self.mavlink_process = None
        self.px4_process = None
        self.status = "stopped"
        self.udp_port = 14550
        self.tcp_port = 5760
        self.current_airframe = None
        
    def cleanup(self):
        """Kill any existing processes"""
        logger.info("Cleaning up existing processes...")
        subprocess.run(['pkill', '-9', 'mavlink-routerd'], stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-9', '-f', 'px4.*sitl'], stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-9', 'gz'], stderr=subprocess.DEVNULL)
        time.sleep(2)
        
    def start_mavlink_router(self):
        """Start MAVLink router"""
        logger.info(f"Starting MAVLink router: UDP {self.udp_port} -> TCP {self.tcp_port}")
        
        cmd = [
            'mavlink-routerd',
            f'0.0.0.0:{self.udp_port}',
            '-t', str(self.tcp_port),
            '-v'
        ]
        
        self.mavlink_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(2)
        
        if self.mavlink_process.poll() is None:
            logger.info("✅ MAVLink router started")
            return True
        else:
            logger.error("❌ MAVLink router failed to start")
            return False
    
    def start_px4(self, airframe="gz_standard_vtol"):
        """Start PX4 SITL"""
        logger.info(f"Starting PX4 SITL ({airframe}, headless)")
        
        cmd = f"cd {self.px4_path} && HEADLESS=1 make px4_sitl {airframe}"
        
        self.px4_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        logger.info("Waiting for PX4 to boot (20 seconds)...")
        time.sleep(20)
        
        if self.px4_process.poll() is None:
            logger.info("✅ PX4 SITL started")
            return True
        else:
            logger.error("❌ PX4 SITL failed to start")
            return False
    
    def configure_mavlink(self):
        """Configure PX4 MAVLink using mavlink_shell.py"""
        logger.info("Configuring PX4 MAVLink connection...")
        
        try:
            mavlink_shell = os.path.join(self.px4_path, "Tools", "mavlink_shell.py")
            
            # Stop all existing MAVLink connections
            logger.info("Stopping existing MAVLink connections...")
            subprocess.run(
                ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                input="mavlink stop-all\n",
                text=True,
                capture_output=True,
                timeout=10
            )
            
            time.sleep(2)
            
            # Start new MAVLink connection to router
            logger.info(f"Starting MAVLink: UDP {self.udp_port} -> 0.0.0.0")
            result = subprocess.run(
                ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                input=f"mavlink start -x -u {self.udp_port} -r 4000000 -t 0.0.0.0\n",
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ MAVLink configured successfully")
                return True
            else:
                logger.warning(f"⚠️ MAVLink configuration may have issues: {result.stderr}")
                return True  # Continue anyway
                
        except Exception as e:
            logger.error(f"Error configuring MAVLink: {e}")
            return False
    
    def start(self, airframe="gz_standard_vtol"):
        """Start the complete SITL system"""
        logger.info("=" * 60)
        logger.info("Starting PX4 SITL + MAVLink Router")
        logger.info("=" * 60)
        
        try:
            # Step 1: Cleanup
            self.cleanup()
            
            # Step 2: Start MAVLink router
            if not self.start_mavlink_router():
                raise Exception("Failed to start MAVLink router")
            
            # Step 3: Start PX4
            if not self.start_px4(airframe):
                raise Exception("Failed to start PX4 SITL")
            
            # Step 4: Configure MAVLink
            self.configure_mavlink()
            
            self.status = "running"
            self.current_airframe = airframe
            logger.info("=" * 60)
            logger.info("✅ SITL System Started Successfully!")
            logger.info(f"🔌 QGC Connection: TCP @ <your-vm-ip>:{self.tcp_port}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SITL: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop the SITL system"""
        logger.info("Stopping SITL system...")
        
        if self.px4_process:
            try:
                os.killpg(os.getpgid(self.px4_process.pid), signal.SIGTERM)
            except:
                pass
        
        if self.mavlink_process:
            try:
                self.mavlink_process.terminate()
            except:
                pass
        
        self.cleanup()
        self.status = "stopped"
        self.current_airframe = None
        logger.info("✅ SITL system stopped")
    
    def get_status(self):
        """Get current status"""
        return {
            "status": self.status,
            "tcp_port": self.tcp_port,
            "udp_port": self.udp_port,
            "airframe": self.current_airframe
        }


if __name__ == "__main__":
    # Test the manager
    manager = SITLManager()
    manager.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
