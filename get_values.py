#!/usr/bin/python3
import pygatt
import time
import json
import paho.mqtt.client as mqtt
import config.creds as creds

#BLE VARIABLES
adapter = pygatt.backends.GATTToolBackend()
sensors = []
values = []

#MQTT VARIABLES
BROKER = '192.168.0.34'
MQTT = mqtt.Client()
MQTT.username_pw_set(username=creds.USERNAME,password=creds.PASSWORD)
MQTT.connect(BROKER)

#GET SENSOR INFO
sensor_file = open('./config/sensors.py', 'r')
sensor_info = sensor_file.readlines()
for line in sensor_info:
    if ' ' in line:
        split = line.strip().split(' ')
        sensors.append({'device': split[0], 'characteristic': split[1]})

print(f"Getting data from {len(sensors)} sensors")
try:
    adapter.start()
    for sensor in sensors:
        print(f"Connecting to device: {sensor['device']}")
        device = adapter.connect(sensor['device'])
        print(f"Reading characteristic: {sensor['characteristic']}")
        value = bytes(device.char_read(sensor['characteristic'])).decode('utf-8')
        values.append({'device': sensor['device'], 'value': value})
finally:
    adapter.stop()

print("Retrieved values:")
print(values)

MQTT.publish("ble/test", json.dumps(values))
time.sleep(1)

MQTT.disconnect()
