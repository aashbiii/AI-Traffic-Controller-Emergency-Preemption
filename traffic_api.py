from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

traffic_data = {
    "active_road": 1,
    "timer": 60,
    "road1": {"vehicles": 0, "emergency": 0},
    "road2": {"vehicles": 0, "emergency": 0}
}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/traffic_status', methods=['GET'])
def get_status():
    return jsonify(traffic_data)

@app.route('/api/update_traffic', methods=['POST'])
def update_traffic():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    print("🔁 Received update from app:", data)  # Debug log

    # Update traffic data based on keys provided
    if "active_road" in data:
        traffic_data["active_road"] = int(data["active_road"])
    if "timer" in data:
        traffic_data["timer"] = int(data["timer"])
    if "road1" in data:
        traffic_data["road1"].update(data["road1"])
    if "road2" in data:
        traffic_data["road2"].update(data["road2"])

    return jsonify({
        "message": "✅ Traffic data updated successfully",
        "data": traffic_data
    })

def run_flask():
    app.run(host="192.168.179.247", port=5000, debug=False)

def start_api_server():
    thread = threading.Thread(target=run_flask)
    thread.setDaemon(True)
    thread.start()
