# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import serial
import time
import json
from datetime import datetime
import requests

app = Flask(__name__)
socketio = SocketIO(app)

# Global variable to store latest readings
latest_data = {}
historical_data = {
    'timestamps': [],
    'pm1': [],
    'pm25': [],
    'pm10': [],
    'co2': [],
    'voc': [],
    'temperature': [],
    'humidity': [],
    'ch2o': [],
    'co': [],
    'o3': [],
    'no2': []
}
# Maximum number of historical data points to keep
MAX_HISTORY = 868

def send_to_thingspeak(data):
    """Send sensor data to ThingSpeak server"""
    try:
        # ThingSpeak payload
        # You can use up to 8 fields in free version
        payload = {
            'api_key': "TPUAJU336ISK78H6",
            'field1': data['temperature'],      # PM2.5
            'field2': data['humidity'],       # PM10
            'field3': data['pm2.5'],        # CO2
            'field4': data['pm10'], # Temperature
            'field5': data['co2'],    # Humidity
            'field6': data['co'],       # CH2O
            'field7': data['o3'],         # CO
            'field8': data['no2']          # O3
        }
        
        # Send data to ThingSpeak
        response = requests.post("https://api.thingspeak.com/update", data=payload, timeout=10)
        
        if response.status_code == 200:
            print("Data successfully sent to ThingSpeak")
        else:
            print(f"Failed to send data to ThingSpeak. Status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to ThingSpeak: {e}")
    except Exception as e:
        print(f"Unexpected error sending data to ThingSpeak: {e}")


def add_to_history(data):
    """Add new data point to historical data"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    historical_data['timestamps'].append(timestamp)
    historical_data['pm1'].append(data['pm1.0'])
    historical_data['pm25'].append(data['pm2.5'])
    historical_data['pm10'].append(data['pm10'])
    historical_data['co2'].append(data['co2'])
    historical_data['voc'].append(data['voc_grade'])
    historical_data['temperature'].append(data['temperature'])
    historical_data['humidity'].append(data['humidity'])
    historical_data['ch2o'].append(data['ch2o'])
    historical_data['co'].append(data['co'])
    historical_data['o3'].append(data['o3'])
    historical_data['no2'].append(data['no2'])
    
    # Keep only last MAX_HISTORY points
    if len(historical_data['timestamps']) > MAX_HISTORY:
        for key in historical_data:
            historical_data[key] = historical_data[key][-MAX_HISTORY:]

@app.route('/')
def index():
    return render_template('index.html')

def setup_uart():
    """Setup UART communication with the sensor"""
    try:
        return serial.Serial(
            port='/dev/serial0',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def calculate_checksum(data):
    """Calculate checksum for verification"""
    total = sum(data[1:25])
    return (~total + 1) & 0xFF

def parse_sensor_data(response):
    """Parse the 26-byte response"""
    if len(response) != 26 or response[0] != 0xFF or response[1] != 0x86:
        return None
    
    if calculate_checksum(response) != response[25]:
        print("Checksum verification failed")
        return None
    
    return {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'pm1.0': (response[2] * 256 + response[3]),
        'pm2.5': (response[4] * 256 + response[5]),
        'pm10': (response[6] * 256 + response[7]),
        'co2': (response[8] * 256 + response[9]),
        'voc_grade': response[10],
        'temperature': ((response[11] * 256 + response[12]) - 500) * 0.1,
        'humidity': (response[13] * 256 + response[14]),
        'ch2o': (response[15] * 256 + response[16]) * 0.001,
        'co': (response[17] * 256 + response[18]) * 0.1,
        'o3': (response[19] * 256 + response[20]) * 0.01,
        'no2': (response[21] * 256 + response[22]) * 0.01
    }

def read_sensor():
    """Read data from sensor and broadcast to websocket clients"""
    ser = setup_uart()
    if not ser:
        return
    
    command = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
    
    while True:
        try:
            ser.reset_input_buffer()
            ser.write(command)
            response = ser.read(26)
            
            if len(response) == 26:
                data = parse_sensor_data(response)
                if data:
                    send_to_thingspeak(data)
                    global latest_data
                    latest_data = data
                    add_to_history(data)
                    socketio.emit('sensor_update', data)
                    time.sleep(600)
            
        except Exception as e:
            print(f"Error reading sensor: {e}")
            time.sleep(1)

@socketio.on('connect')
def handle_connect():
    """Send historical data when a client connects"""
    socketio.emit('historical_data', historical_data)
    if latest_data:
        socketio.emit('sensor_update', latest_data)

if __name__ == '__main__':
    # Start sensor reading in a separate thread
    sensor_thread = threading.Thread(target=read_sensor, daemon=True)
    sensor_thread.start()
    
    # Run the web server
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
