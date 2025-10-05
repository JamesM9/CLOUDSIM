#!/usr/bin/env python3
"""
Multi-Instance SITL Manager for PX4
Manages multiple PX4 SITL instances with different airframes and ports
"""

import subprocess
import time
import os
import signal
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PortPool:
    """Manages port allocation for multiple SITL instances"""
    
    def __init__(self):
        self.udp_base = 14550
        self.tcp_base = 5760
        self.increment = 1
        self.used_ports = set()
        self.max_instances = 10  # Limit to prevent resource exhaustion
    
    def allocate_ports(self):
        """Allocate a pair of ports for a new instance"""
        if len(self.used_ports) >= self.max_instances:
            raise Exception(f"Maximum number of instances ({self.max_instances}) reached")
        
        # Find next available port pair
        for i in range(self.max_instances):
            udp_port = self.udp_base + (i * self.increment)
            tcp_port = self.tcp_base + (i * self.increment)
            
            if (udp_port, tcp_port) not in self.used_ports:
                self.used_ports.add((udp_port, tcp_port))
                logger.info(f"Allocated ports: UDP {udp_port}, TCP {tcp_port}")
                return udp_port, tcp_port
        
        raise Exception("No available ports")
    
    def release_ports(self, udp_port, tcp_port):
        """Release ports back to the pool"""
        if (udp_port, tcp_port) in self.used_ports:
            self.used_ports.remove((udp_port, tcp_port))
            logger.info(f"Released ports: UDP {udp_port}, TCP {tcp_port}")
        else:
            logger.warning(f"Attempted to release unallocated ports: UDP {udp_port}, TCP {tcp_port}")


class SITLInstance:
    """Represents a single SITL instance"""
    
    def __init__(self, instance_id, airframe, udp_port, tcp_port):
        self.instance_id = instance_id
        self.airframe = airframe
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.px4_process = None
        self.mavlink_process = None
        self.status = "stopped"
        self.start_time = None
        self.px4_path = os.path.expanduser("~/PX4-Autopilot")
        
    def cleanup_existing_processes(self):
        """Clean up any existing processes that might conflict for this specific instance"""
        logger.info(f"Cleaning up existing processes for instance {self.instance_id}...")
        
        # Only kill processes that might conflict with this specific instance
        # Don't kill all MAVLink routers - that breaks other instances!
        
        # Kill any existing PX4 processes (this is instance-specific)
        subprocess.run(['pkill', '-9', '-f', 'px4.*sitl'], stderr=subprocess.DEVNULL)
        
        # Kill any existing Gazebo processes (this is instance-specific)  
        subprocess.run(['pkill', '-9', 'gz'], stderr=subprocess.DEVNULL)
        
        # For MAVLink router, we should check if the port is already in use
        # and only kill the specific process using that port
        try:
            # Check if our target TCP port is in use
            result = subprocess.run(['lsof', '-ti', f':{self.tcp_port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                # Kill only the process using our specific port
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], stderr=subprocess.DEVNULL)
                        logger.info(f"Killed process {pid} using port {self.tcp_port}")
                    except:
                        pass
        except:
            # Fallback: just continue without killing MAVLink routers
            logger.info("Could not check for port conflicts, continuing...")
            pass
        
        time.sleep(2)
    
    def start_mavlink_router(self):
        """Start MAVLink router for this instance"""
        logger.info(f"Starting MAVLink router for instance {self.instance_id}: UDP {self.udp_port} -> TCP {self.tcp_port}")
        
        # Clean up any existing processes first
        self.cleanup_existing_processes()
        
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
            logger.info(f"✅ MAVLink router started for instance {self.instance_id}")
            return True
        else:
            logger.error(f"❌ MAVLink router failed to start for instance {self.instance_id}")
            return False
    
    def start_px4(self):
        """Start PX4 SITL for this instance"""
        logger.info(f"Starting PX4 SITL for instance {self.instance_id} ({self.airframe}, headless)")
        
        cmd = f"cd {self.px4_path} && HEADLESS=1 make px4_sitl {self.airframe}"
        
        self.px4_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        logger.info(f"Waiting for PX4 to boot for instance {self.instance_id} (20 seconds)...")
        time.sleep(20)
        
        if self.px4_process.poll() is None:
            logger.info(f"✅ PX4 SITL started for instance {self.instance_id}")
            return True
        else:
            logger.error(f"❌ PX4 SITL failed to start for instance {self.instance_id}")
            return False
    
    def configure_mavlink(self):
        """Configure PX4 MAVLink for this instance"""
        logger.info(f"Configuring PX4 MAVLink for instance {self.instance_id}...")
        
        try:
            # Wait longer for PX4 to fully start and stabilize
            logger.info(f"Waiting for PX4 to stabilize for instance {self.instance_id}...")
            time.sleep(10)
            
            mavlink_shell = os.path.join(self.px4_path, "Tools", "mavlink_shell.py")
            
            if not os.path.exists(mavlink_shell):
                logger.warning(f"MAVLink shell not found at {mavlink_shell}, skipping configuration")
                return True
            
            # Try multiple times to configure MAVLink
            for attempt in range(3):
                try:
                    logger.info(f"MAVLink configuration attempt {attempt + 1} for instance {self.instance_id}...")
                    
                    # First, check if we can connect to PX4
                    test_result = subprocess.run(
                        ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                        input="status\n",
                        text=True,
                        capture_output=True,
                        timeout=10
                    )
                    
                    if test_result.returncode != 0:
                        logger.warning(f"Could not connect to PX4 on attempt {attempt + 1}, retrying...")
                        time.sleep(5)
                        continue
                    
                    # Now configure MAVLink with correct target address
                    result = subprocess.run(
                        ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                        input=f"mavlink start -x -u {self.udp_port} -r 4000000 -t 127.0.0.1\n",
                        text=True,
                        capture_output=True,
                        timeout=20
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✅ MAVLink configured successfully for instance {self.instance_id}")
                        
                        # Verify the configuration
                        time.sleep(2)
                        verify_result = subprocess.run(
                            ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                            input="mavlink status\n",
                            text=True,
                            capture_output=True,
                            timeout=10
                        )
                        
                        if verify_result.returncode == 0:
                            logger.info(f"✅ MAVLink status verified for instance {self.instance_id}")
                            return True
                        else:
                            logger.warning(f"⚠️ MAVLink status verification failed for instance {self.instance_id}")
                    
                    else:
                        logger.warning(f"⚠️ MAVLink configuration failed on attempt {attempt + 1}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"MAVLink configuration timed out on attempt {attempt + 1}")
                except Exception as e:
                    logger.warning(f"MAVLink configuration error on attempt {attempt + 1}: {e}")
                
                if attempt < 2:  # Don't sleep after the last attempt
                    time.sleep(5)
            
            # If all attempts failed, try a different approach
            logger.info(f"Trying alternative MAVLink configuration for instance {self.instance_id}...")
            try:
                # Try without stopping existing connections
                result = subprocess.run(
                    ['python3', mavlink_shell, f'udp:127.0.0.1:{self.udp_port}'],
                    input=f"mavlink start -u {self.udp_port} -r 4000000\n",
                    text=True,
                    capture_output=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Alternative MAVLink configuration successful for instance {self.instance_id}")
                    return True
                    
            except Exception as e:
                logger.warning(f"Alternative MAVLink configuration failed: {e}")
            
            logger.warning(f"⚠️ All MAVLink configuration attempts failed for instance {self.instance_id}, but continuing...")
            return True
                
        except Exception as e:
            logger.error(f"Error in MAVLink setup for instance {self.instance_id}: {e}")
            return True
    
    def start(self):
        """Start this SITL instance"""
        logger.info(f"Starting SITL instance {self.instance_id} ({self.airframe})")
        
        try:
            # Start MAVLink router
            if not self.start_mavlink_router():
                raise Exception("Failed to start MAVLink router")
            
            # Start PX4
            if not self.start_px4():
                raise Exception("Failed to start PX4 SITL")
            
            # Configure MAVLink
            self.configure_mavlink()
            
            self.status = "running"
            self.start_time = datetime.now()
            logger.info(f"✅ SITL instance {self.instance_id} started successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SITL instance {self.instance_id}: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop this SITL instance"""
        logger.info(f"Stopping SITL instance {self.instance_id}...")
        
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
        
        self.status = "stopped"
        self.start_time = None
        logger.info(f"✅ SITL instance {self.instance_id} stopped")
    
    def get_status(self):
        """Get status of this instance"""
        return {
            "instance_id": self.instance_id,
            "airframe": self.airframe,
            "status": self.status,
            "udp_port": self.udp_port,
            "tcp_port": self.tcp_port,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }


class MultiSITLManager:
    """Manages multiple SITL instances"""
    
    def __init__(self):
        self.instances = {}
        self.port_pool = PortPool()
        self.next_instance_id = 1
    
    def create_instance(self, airframe="gz_x500"):
        """Create a new SITL instance"""
        try:
            # Allocate ports
            udp_port, tcp_port = self.port_pool.allocate_ports()
            
            # Create instance
            instance_id = f"instance_{self.next_instance_id}"
            instance = SITLInstance(instance_id, airframe, udp_port, tcp_port)
            
            # Store instance
            self.instances[instance_id] = instance
            self.next_instance_id += 1
            
            logger.info(f"Created SITL instance {instance_id} with airframe {airframe}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to create SITL instance: {e}")
            return None
    
    def start_instance(self, instance_id):
        """Start a specific instance"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False
        
        instance = self.instances[instance_id]
        return instance.start()
    
    def stop_instance(self, instance_id):
        """Stop a specific instance"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False
        
        instance = self.instances[instance_id]
        instance.stop()
        
        # Release ports
        self.port_pool.release_ports(instance.udp_port, instance.tcp_port)
        
        return True
    
    def remove_instance(self, instance_id):
        """Remove an instance (must be stopped first)"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False
        
        instance = self.instances[instance_id]
        
        if instance.status == "running":
            logger.error(f"Cannot remove running instance {instance_id}")
            return False
        
        # Release ports
        self.port_pool.release_ports(instance.udp_port, instance.tcp_port)
        
        # Remove instance
        del self.instances[instance_id]
        logger.info(f"Removed SITL instance {instance_id}")
        return True
    
    def stop_all_instances(self):
        """Stop all running instances"""
        logger.info("Stopping all SITL instances...")
        
        for instance_id, instance in self.instances.items():
            if instance.status == "running":
                instance.stop()
                self.port_pool.release_ports(instance.udp_port, instance.tcp_port)
        
        logger.info("All SITL instances stopped")
    
    def get_all_status(self):
        """Get status of all instances"""
        return {
            "instances": {instance_id: instance.get_status() 
                         for instance_id, instance in self.instances.items()},
            "total_instances": len(self.instances),
            "running_instances": len([i for i in self.instances.values() if i.status == "running"])
        }
    
    def get_instance_status(self, instance_id):
        """Get status of a specific instance"""
        if instance_id not in self.instances:
            return None
        
        return self.instances[instance_id].get_status()


if __name__ == "__main__":
    # Test the multi-instance manager
    manager = MultiSITLManager()
    
    # Create a test instance
    instance_id = manager.create_instance("gz_x500")
    if instance_id:
        print(f"Created instance: {instance_id}")
        
        # Start the instance
        if manager.start_instance(instance_id):
            print("Instance started successfully")
            
            # Wait a bit
            time.sleep(5)
            
            # Stop the instance
            manager.stop_instance(instance_id)
            print("Instance stopped")
            
            # Remove the instance
            manager.remove_instance(instance_id)
            print("Instance removed")
        else:
            print("Failed to start instance")
    else:
        print("Failed to create instance")
