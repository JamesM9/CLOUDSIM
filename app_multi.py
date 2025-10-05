#!/usr/bin/env python3
"""
Multi-Instance Flask Web GUI for PX4 SITL
Supports multiple SITL instances with different airframes and ports
"""

from flask import Flask, render_template, jsonify, request
import logging
import requests
from multi_sitl_manager import MultiSITLManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
multi_sitl = MultiSITLManager()


def get_public_ip():
    """Get the VM's public IP"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json().get('ip', 'Unknown')
    except:
        return 'Unknown'


@app.route('/')
def index():
    """Main page"""
    return render_template('index_multi.html')


@app.route('/api/instances')
def api_get_instances():
    """Get all instances status"""
    try:
        status = multi_sitl.get_all_status()
        status['public_ip'] = get_public_ip()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting instances status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances', methods=['POST'])
def api_create_instance():
    """Create a new SITL instance"""
    try:
        # Get airframe from request data
        data = request.get_json() or {}
        airframe = data.get('airframe', 'gz_x500')
        
        # Validate airframe
        valid_airframes = [
            'gz_x500', 'gz_standard_vtol', 'gz_rc_cessna', 'gz_advanced_plane',
            'gz_quadtailsitter', 'gz_tiltrotor', 'gz_rover_differential',
            'gz_rover_ackermann', 'gz_rover_mecanum'
        ]
        
        if airframe not in valid_airframes:
            return jsonify({"success": False, "error": f"Invalid airframe: {airframe}"}), 400
        
        # Create instance
        instance_id = multi_sitl.create_instance(airframe)
        
        if instance_id:
            return jsonify({
                "success": True,
                "message": f"SITL instance created with {airframe}",
                "instance_id": instance_id,
                "airframe": airframe
            })
        else:
            return jsonify({"success": False, "error": "Failed to create instance"}), 500
            
    except Exception as e:
        logger.error(f"Error creating instance: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances/<instance_id>/start', methods=['POST'])
def api_start_instance(instance_id):
    """Start a specific SITL instance"""
    try:
        success = multi_sitl.start_instance(instance_id)
        
        if success:
            instance_status = multi_sitl.get_instance_status(instance_id)
            return jsonify({
                "success": True,
                "message": f"SITL instance {instance_id} started successfully",
                "instance_id": instance_id,
                "public_ip": get_public_ip(),
                "tcp_port": instance_status['tcp_port'],
                "airframe": instance_status['airframe']
            })
        else:
            return jsonify({"success": False, "error": f"Failed to start instance {instance_id}"}), 500
            
    except Exception as e:
        logger.error(f"Error starting instance {instance_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances/<instance_id>/stop', methods=['POST'])
def api_stop_instance(instance_id):
    """Stop a specific SITL instance"""
    try:
        success = multi_sitl.stop_instance(instance_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"SITL instance {instance_id} stopped successfully",
                "instance_id": instance_id
            })
        else:
            return jsonify({"success": False, "error": f"Failed to stop instance {instance_id}"}), 500
            
    except Exception as e:
        logger.error(f"Error stopping instance {instance_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances/<instance_id>')
def api_get_instance(instance_id):
    """Get a specific SITL instance status"""
    try:
        instance_status = multi_sitl.get_instance_status(instance_id)
        
        if instance_status:
            instance_status['public_ip'] = get_public_ip()
            return jsonify(instance_status)
        else:
            return jsonify({"success": False, "error": f"Instance {instance_id} not found"}), 404
            
    except Exception as e:
        logger.error(f"Error getting instance {instance_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances/<instance_id>', methods=['DELETE'])
def api_remove_instance(instance_id):
    """Remove a specific SITL instance"""
    try:
        success = multi_sitl.remove_instance(instance_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"SITL instance {instance_id} removed successfully",
                "instance_id": instance_id
            })
        else:
            return jsonify({"success": False, "error": f"Failed to remove instance {instance_id}"}), 500
            
    except Exception as e:
        logger.error(f"Error removing instance {instance_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/instances/stop-all', methods=['POST'])
def api_stop_all_instances():
    """Stop all SITL instances"""
    try:
        multi_sitl.stop_all_instances()
        return jsonify({
            "success": True,
            "message": "All SITL instances stopped successfully"
        })
    except Exception as e:
        logger.error(f"Error stopping all instances: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Legacy endpoints for backward compatibility
@app.route('/api/status')
def api_status():
    """Legacy status endpoint - returns first instance or empty"""
    try:
        status = multi_sitl.get_all_status()
        if status['total_instances'] > 0:
            # Return status of first instance for backward compatibility
            first_instance = list(status['instances'].values())[0]
            first_instance['public_ip'] = get_public_ip()
            return jsonify(first_instance)
        else:
            return jsonify({
                "status": "stopped",
                "tcp_port": 5760,
                "udp_port": 14550,
                "airframe": None,
                "public_ip": get_public_ip()
            })
    except Exception as e:
        logger.error(f"Error getting legacy status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/start', methods=['POST'])
def api_start():
    """Legacy start endpoint - creates and starts a new instance"""
    try:
        # Get airframe from request data
        data = request.get_json() or {}
        airframe = data.get('airframe', 'gz_x500')
        
        # Validate airframe
        valid_airframes = [
            'gz_x500', 'gz_standard_vtol', 'gz_rc_cessna', 'gz_advanced_plane',
            'gz_quadtailsitter', 'gz_tiltrotor', 'gz_rover_differential',
            'gz_rover_ackermann', 'gz_rover_mecanum'
        ]
        
        if airframe not in valid_airframes:
            return jsonify({"success": False, "error": f"Invalid airframe: {airframe}"}), 400
        
        # Create and start instance
        instance_id = multi_sitl.create_instance(airframe)
        
        if instance_id:
            success = multi_sitl.start_instance(instance_id)
            
            if success:
                instance_status = multi_sitl.get_instance_status(instance_id)
                return jsonify({
                    "success": True,
                    "message": f"SITL started successfully with {airframe}",
                    "public_ip": get_public_ip(),
                    "tcp_port": instance_status['tcp_port'],
                    "airframe": airframe,
                    "instance_id": instance_id
                })
            else:
                # Clean up failed instance
                multi_sitl.remove_instance(instance_id)
                return jsonify({"success": False, "error": "Failed to start"}), 500
        else:
            return jsonify({"success": False, "error": "Failed to create instance"}), 500
            
    except Exception as e:
        logger.error(f"Error starting SITL: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Legacy stop endpoint - stops all instances"""
    try:
        multi_sitl.stop_all_instances()
        return jsonify({"success": True, "message": "All SITL instances stopped"})
    except Exception as e:
        logger.error(f"Error stopping SITL: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("PX4 SITL Multi-Instance Web GUI")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
