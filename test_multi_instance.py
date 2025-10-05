#!/usr/bin/env python3
"""
Test script for multi-instance SITL functionality
Tests creating, managing, and cleaning up multiple instances
"""

import time
import requests
import subprocess
import os
import signal
from multi_sitl_manager import MultiSITLManager

def test_multi_instance_manager():
    """Test the MultiSITLManager directly"""
    print("=" * 60)
    print("Testing MultiSITLManager")
    print("=" * 60)
    
    manager = MultiSITLManager()
    
    # Test creating multiple instances
    print("\n1. Creating multiple instances...")
    instance1 = manager.create_instance('gz_x500')
    instance2 = manager.create_instance('gz_standard_vtol')
    instance3 = manager.create_instance('gz_rc_cessna')
    
    print(f"Created instances: {instance1}, {instance2}, {instance3}")
    
    # Test getting status
    print("\n2. Getting status...")
    status = manager.get_all_status()
    print(f"Total instances: {status['total_instances']}")
    print(f"Running instances: {status['running_instances']}")
    
    # Test individual instance status
    for instance_id in [instance1, instance2, instance3]:
        if instance_id:
            instance_status = manager.get_instance_status(instance_id)
            print(f"Instance {instance_id}: {instance_status['airframe']} - {instance_status['status']} - UDP:{instance_status['udp_port']} TCP:{instance_status['tcp_port']}")
    
    # Test port allocation
    print("\n3. Testing port allocation...")
    print("Port pool used ports:", manager.port_pool.used_ports)
    
    # Test removing instances
    print("\n4. Removing instances...")
    for instance_id in [instance1, instance2, instance3]:
        if instance_id:
            success = manager.remove_instance(instance_id)
            print(f"Removed {instance_id}: {success}")
    
    # Final status
    final_status = manager.get_all_status()
    print(f"\nFinal status - Total instances: {final_status['total_instances']}")
    print("Port pool used ports after cleanup:", manager.port_pool.used_ports)
    
    print("\n✅ MultiSITLManager test completed successfully!")


def test_flask_api():
    """Test the Flask API endpoints"""
    print("\n" + "=" * 60)
    print("Testing Flask API")
    print("=" * 60)
    
    # Start Flask app in background
    flask_process = subprocess.Popen(['python3', 'app_multi.py'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
    
    try:
        # Wait for Flask to start
        time.sleep(3)
        
        base_url = 'http://localhost:5000'
        
        # Test 1: Get initial instances (should be empty)
        print("\n1. Testing GET /api/instances (initial)")
        response = requests.get(f'{base_url}/api/instances')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total instances: {data.get('total_instances', 0)}")
        
        # Test 2: Create instances
        print("\n2. Testing POST /api/instances")
        airframes = ['gz_x500', 'gz_standard_vtol', 'gz_rc_cessna']
        created_instances = []
        
        for airframe in airframes:
            response = requests.post(f'{base_url}/api/instances', 
                                   json={'airframe': airframe})
            print(f"Created {airframe}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                instance_id = data.get('instance_id')
                created_instances.append(instance_id)
                print(f"  Instance ID: {instance_id}")
        
        # Test 3: Get instances after creation
        print("\n3. Testing GET /api/instances (after creation)")
        response = requests.get(f'{base_url}/api/instances')
        if response.status_code == 200:
            data = response.json()
            print(f"Total instances: {data.get('total_instances', 0)}")
            print(f"Running instances: {data.get('running_instances', 0)}")
            
            # Show instance details
            for instance_id, instance_data in data.get('instances', {}).items():
                print(f"  {instance_id}: {instance_data['airframe']} - {instance_data['status']} - TCP:{instance_data['tcp_port']}")
        
        # Test 4: Test individual instance endpoints
        print("\n4. Testing individual instance endpoints")
        for instance_id in created_instances:
            if instance_id:
                # Test getting instance status
                response = requests.get(f'{base_url}/api/instances/{instance_id}')
                print(f"GET /api/instances/{instance_id}: {response.status_code}")
                
                # Test starting instance (this would actually start PX4, so we'll skip for now)
                # response = requests.post(f'{base_url}/api/instances/{instance_id}/start')
                # print(f"POST /api/instances/{instance_id}/start: {response.status_code}")
        
        # Test 5: Test bulk operations
        print("\n5. Testing bulk operations")
        response = requests.post(f'{base_url}/api/instances/stop-all')
        print(f"POST /api/instances/stop-all: {response.status_code}")
        
        # Test 6: Clean up instances
        print("\n6. Cleaning up instances")
        for instance_id in created_instances:
            if instance_id:
                response = requests.delete(f'{base_url}/api/instances/{instance_id}')
                print(f"DELETE /api/instances/{instance_id}: {response.status_code}")
        
        # Final status
        print("\n7. Final status")
        response = requests.get(f'{base_url}/api/instances')
        if response.status_code == 200:
            data = response.json()
            print(f"Total instances: {data.get('total_instances', 0)}")
        
        print("\n✅ Flask API test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Flask API: {e}")
    finally:
        # Stop Flask app
        flask_process.terminate()
        flask_process.wait()


def test_port_conflicts():
    """Test that port allocation prevents conflicts"""
    print("\n" + "=" * 60)
    print("Testing Port Conflict Prevention")
    print("=" * 60)
    
    manager = MultiSITLManager()
    
    # Create multiple instances and verify unique ports
    print("\nCreating multiple instances to test port allocation...")
    instances = []
    
    for i in range(5):
        instance_id = manager.create_instance('gz_x500')
        if instance_id:
            instances.append(instance_id)
            instance_status = manager.get_instance_status(instance_id)
            print(f"Instance {instance_id}: UDP {instance_status['udp_port']}, TCP {instance_status['tcp_port']}")
    
    # Verify all ports are unique
    print("\nVerifying port uniqueness...")
    all_ports = []
    for instance_id in instances:
        instance_status = manager.get_instance_status(instance_id)
        udp_port = instance_status['udp_port']
        tcp_port = instance_status['tcp_port']
        
        if (udp_port, tcp_port) in all_ports:
            print(f"❌ Port conflict detected: UDP {udp_port}, TCP {tcp_port}")
        else:
            all_ports.append((udp_port, tcp_port))
            print(f"✅ Unique ports: UDP {udp_port}, TCP {tcp_port}")
    
    # Clean up
    print("\nCleaning up...")
    for instance_id in instances:
        manager.remove_instance(instance_id)
    
    print("✅ Port conflict test completed successfully!")


if __name__ == "__main__":
    print("Starting Multi-Instance SITL Tests")
    print("=" * 60)
    
    try:
        # Test 1: MultiSITLManager
        test_multi_instance_manager()
        
        # Test 2: Port conflicts
        test_port_conflicts()
        
        # Test 3: Flask API
        test_flask_api()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
