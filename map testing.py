import serial
import threading
import time
import webbrowser
import os
from collections import deque
from flask import Flask, jsonify, render_template_string

# Environment fix for Raspberry Pi Desktop (Wayland/X11)
os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- Smoothing Buffers (Stores last 5 readings to stop jitter) ---
lat_buffer = deque(maxlen=5)
lon_buffer = deque(maxlen=5)

# --- Shared Data Store ---
gps_data = {
    "lat": 8.170503, 
    "lon": 4.244543,
    "speed": 0.0,
    "heading": 0.0,
    "fix": False,
}

# ============================================
# GPS Reader Logic
# ============================================
def parse_gnrmc(sentence):
    try:
        parts = sentence.split(',')
        if len(parts) < 9 or parts[2] != 'A':
            return None
        
        # Latitude Conversion
        lat_raw = float(parts[3])
        lat_deg = int(lat_raw / 100)
        lat_min = lat_raw - lat_deg * 100
        lat = lat_deg + (lat_min / 60.0)
        if parts[4] == 'S': lat = -lat
        
        # Longitude Conversion
        lon_raw = float(parts[5])
        lon_deg = int(lon_raw / 100)
        lon_min = lon_raw - lon_deg * 100
        lon = lon_deg + (lon_min / 60.0)
        if parts[6] == 'W': lon = -lon
        
        speed = float(parts[7]) * 1.852 if parts[7] else 0.0
        heading = float(parts[8]) if parts[8] else 0.0
        
        return lat, lon, speed, heading
    except Exception:
        return None

def gps_thread_func():
    # Using the /dev/gpsport alias from our udev rule
    port = '/dev/gpsport' 
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"📡 GPS Thread Active on {port}")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('ascii', errors='replace').strip()
                if line.startswith('$GNRMC') or line.startswith('$GPRMC'):
                    result = parse_gnrmc(line)
                    if result:
                        new_lat, new_lon, speed, heading = result
                        
                        # Apply Smoothing Filter
                        lat_buffer.append(new_lat)
                        lon_buffer.append(new_lon)
                        
                        gps_data["lat"] = sum(lat_buffer) / len(lat_buffer)
                        gps_data["lon"] = sum(lon_buffer) / len(lon_buffer)
                        gps_data["speed"] = speed
                        gps_data["heading"] = heading
                        gps_data["fix"] = True
            time.sleep(0.1)
    except Exception as e:
        print(f"⚠️ GPS Error: {e}")

# Start background GPS tracking
threading.Thread(target=gps_thread_func, daemon=True).start()

# ============================================
# Flask Web Server
# ============================================
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Samfred Robotics - HD Map</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <style>
        body { margin: 0; background: #050505; font-family: 'Courier New', monospace; color: #00ff88; overflow: hidden; }
        #header { background: #111; padding: 12px; border-bottom: 2px solid #00ff88; text-align: center; font-weight: bold; letter-spacing: 2px; }
        #map { height: calc(100vh - 110px); width: 100%; }
        #stats { background: #111; padding: 15px; display: flex; justify-content: space-around; border-top: 2px solid #00ff88; }
        .stat-box { text-align: center; }
        .label { font-size: 10px; color: #666; display: block; margin-bottom: 5px; }
        .value { font-size: 16px; color: white; }
    </style>
</head>
<body>
    <div id="header">🛰️ SAMFRED ROBOTICS - HD SATELLITE NAV</div>
    <div id="map"></div>
    <div id="stats">
        <div class="stat-box"><span class="label">LATITUDE</span><span id="lat" class="value">--</span></div>
        <div class="stat-box"><span class="label">LONGITUDE</span><span id="lon" class="value">--</span></div>
        <div class="stat-box"><span class="label">SPEED (KM/H)</span><span id="speed" class="value">0.0</span></div>
        <div class="stat-box"><span class="label">GPS STATUS</span><span id="fix" class="value" style="color:red;">OFFLINE</span></div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Start Map at zoom level 20 (Deep Zoom)
        var map = L.map('map', { maxZoom: 22 }).setView([8.170503, 4.244543], 20);
        
        // Google Satellite Hybrid (S=Satellite, H=High-Res Hybrid)
        L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
            maxZoom: 22,
            subdomains:['mt0','mt1','mt2','mt3'],
            attribution: '&copy; Google Maps'
        }).addTo(map);

        var robotMarker = L.circleMarker([8.170503, 4.244543], {
            radius: 8, color: 'white', weight: 2, fillColor: '#00ff88', fillOpacity: 1
        }).addTo(map);

        var path = L.polyline([], {color: '#00ff88', weight: 3, opacity: 0.7}).addTo(map);

        function updateData() {
            fetch('/data')
                .then(r => r.json())
                .then(data => {
                    if (data.fix) {
                        var pos = [data.lat, data.lon];
                        robotMarker.setLatLng(pos);
                        path.addLatLng(pos);
                        map.panTo(pos);
                        
                        document.getElementById('lat').innerText = data.lat.toFixed(6);
                        document.getElementById('lon').innerText = data.lon.toFixed(6);
                        document.getElementById('speed').innerText = data.speed.toFixed(1);
                        document.getElementById('fix').innerText = "LIVE FIX";
                        document.getElementById('fix').style.color = "#00ff88";
                    }
                });
        }
        setInterval(updateData, 800); // Faster update for robot tracking
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/data')
def get_data():
    return jsonify(gps_data)

def start_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Thread(target=start_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)