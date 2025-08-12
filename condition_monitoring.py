import time
import configparser
import os
import requests
import board
import adafruit_dht
import RPi.GPIO as GPIO
import signal
import sys

# --------------------------
# Load Cumulocity config
# --------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

C8Y_BASE_URL = config["Cumulocity"]["base_url"]
AUTH_HEADER = {
    "Authorization": config["Cumulocity"]["authorization"],
    "Content-Type": "application/json",
    "Accept": "application/json"
}
DEVICE_ID = "<device ID>"

# --------------------------
# DHT11 setup on GPIO4
# --------------------------
dht_device = adafruit_dht.DHT11(board.D4)

# --------------------------
# Photo sensor DO pin setup
# --------------------------
PHOTO_PIN = 17  # GPIO17 (physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PHOTO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --------------------------
# Send temp/humidity measurement
# --------------------------
def send_measurement_temp_hum(temperature_c, humidity):
    payload = {
        "source": {"id": DEVICE_ID},
        "type": "EnvMeasurement",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "c8y_Temperature": {"T": {"value": temperature_c, "unit": "C"}},
        "c8y_Humidity": {"H": {"value": humidity, "unit": "%"}}
    }
    try:
        r = requests.post(f"{C8Y_BASE_URL}/measurement/measurements",
                          json=payload, headers=AUTH_HEADER, timeout=10)
        if r.status_code in (200, 201):
            print(f"✅ Temp/Hum sent: {temperature_c}°C, {humidity}%")
        else:
            print(f"❌ Temp/Hum send failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"⚠ Error sending Temp/Hum: {e}")

# --------------------------
# Send photo sensor event (light detected)
# --------------------------
def send_photo_event():
    payload = {
        "source": {"id": DEVICE_ID},
        "type": "c8y_Light",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "text": "Exposed to light",
        "c8y_Light": {"value": 0}  # per your inverted logic
    }
    try:
        r = requests.post(f"{C8Y_BASE_URL}/event/events",
                          json=payload, headers=AUTH_HEADER, timeout=10)
        if r.status_code in (200, 201):
            print("💡 Light detected event sent")
        else:
            print(f"❌ Light event send failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"⚠ Error sending light event: {e}")

# --------------------------
# Graceful exit
# --------------------------
def signal_handler(sig, frame):
    print("\n👋 Exiting gracefully...")
    dht_device.exit()
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("📡 Temp/Hum: measurement every 5s | Light: send EVENT only when detected...")

while True:
    try:
        # Temperature & Humidity every loop
        temp_c = dht_device.temperature
        hum = dht_device.humidity
        if temp_c is not None and hum is not None:
            send_measurement_temp_hum(temp_c, hum)

        # Photo sensor — trigger only if exposed to light
        raw_state = GPIO.input(PHOTO_PIN)       # raw = 1 if light detected (module logic)
        inverted_state = 0 if raw_state == 1 else 1  # inverted

        if inverted_state == 0:  # means light detected (in inverted logic)
            send_photo_event()

    except RuntimeError as e:
        print(f"⚠ DHT11 read error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        dht_device.exit()
        GPIO.cleanup()
        break

    time.sleep(5)
