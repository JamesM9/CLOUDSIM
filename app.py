#!/usr/bin/env python3
"""
Simple Flask Web GUI for PX4 SITL
"""

from flask import Flask, render_template, jsonify, request
import logging
import requests
from sitl_manager import SITLManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sitl = SITLManager()


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
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Get SITL status"""
    status = sitl.get_status()
    status['public_ip'] = get_public_ip()
    return jsonify(status)


@app.route('/api/start', methods=['POST'])
def api_start():
    """Start SITL"""
    try:
        if sitl.status == "running":
            return jsonify({"success": False, "error": "Already running"}), 400
        
        # Get airframe from request data
        data = request.get_json() or {}
        airframe = data.get('airframe', 'gz_standard_vtol')
        
        # Validate airframe
        valid_airframes = [
            'gz_standard_vtol', 'gz_rc_cessna', 'gz_advanced_plane',
            'gz_quadtailsitter', 'gz_tiltrotor', 'gz_rover_differential',
            'gz_rover_ackermann', 'gz_rover_mecanum'
        ]
        
        if airframe not in valid_airframes:
            return jsonify({"success": False, "error": f"Invalid airframe: {airframe}"}), 400
        
        success = sitl.start(airframe)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"SITL started successfully with {airframe}",
                "public_ip": get_public_ip(),
                "tcp_port": sitl.tcp_port,
                "airframe": airframe
            })
        else:
            return jsonify({"success": False, "error": "Failed to start"}), 500
            
    except Exception as e:
        logger.error(f"Error starting SITL: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop SITL"""
    try:
        sitl.stop()
        return jsonify({"success": True, "message": "SITL stopped"})
    except Exception as e:
        logger.error(f"Error stopping SITL: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("PX4 SITL Web GUI")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
