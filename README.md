# ZPHS01B - Multi-in-One Air Quality Module

ZPHS01B is a multi-in-one air quality module, integrating:
- Laser dust sensor
- Infrared carbon dioxide sensor
- Electrochemical formaldehyde sensor
- Electrochemical ozone sensor
- Electrochemical carbon monoxide sensor
- VOC sensor
- NO2 sensor
- Temperature and humidity sensor

It can accurately measure the concentration of various gases in the air and communicates via a UART (TTL level) interface.

## Hardware Setup
This module was used with a **Raspberry Pi 3 Model B**.

## Software Setup

### Step 1: Install Required Libraries
Make sure to install the required libraries listed in the `requirements.txt` file. It's recommended to use a virtual environment for this step:

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: View Sensor Data in Terminal
Use the `printValues.py` script to see the sensor output in the terminal:
```bash
python3 printValues.py
```

### Step 3: Visualize Sensor Data in Web UI
Use the `app.py` program to visualize the sensor data through a WebUI. The application runs on port 8080.

1. Start the WebUI:
   ```bash
   python3 app.py
   ```

2. Access the WebUI in a browser using the Raspberry Pi's IP address:
   ```
   http://<Raspberry Pi's IP>:8080
   ```

## Notes
- Ensure that the Raspberry Pi and your client device are on the same network for accessing the WebUI.
- Properly handle and maintain the sensors for accurate measurements.

---
For any issues or inquiries, please refer to the documentation or contact the support team.

