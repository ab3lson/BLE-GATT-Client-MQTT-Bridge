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
notification = ""

#MQTT VARIABLES
BROKER = '192.168.0.34'
MQTT_TOPIC = 'ble/test'
MQTT = mqtt.Client()
MQTT.username_pw_set(username=creds.USERNAME,password=creds.PASSWORD)
MQTT.connect(BROKER)

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    global notification
    notification = bytes(value).decode('utf-8')

#GET SENSOR INFO
print("Getting sensor information...")
sensor_file = open('./config/sensors_v2.py', 'r')
sensor_info = sensor_file.readlines()
for line in sensor_info:
    if ' ' in line and '#' not in line:
        try:
            split = line.strip().split(' ')
            if (split[2] != None): sensors.append({'device': split[0], 'characteristic': split[1], 'notif': True})
            else: sensors.append({'device': split[0], 'characteristic': split[1], 'notif': False})
        except:
            print(f"[ERROR] Bad sensor formatting: {line.strip()}\nTry formatting like: MAC_ADDRESS CHAR_UUID [notif/char]")


print(f"Getting data from {len(sensors)} sensors!")
for sensor in sensors:
    connection_attempts = 0
    while connection_attempts < 3:
        print(f"- Connection attempt #{connection_attempts + 1}")
        adapter.start()
        try:
            if not sensor["notif"]: # Reads the characteristic data directly, if supported
                print(f"[INFO] Connecting to device: {sensor['device']}")
                device = adapter.connect(sensor['device'])
                print(f"[INFO] Reading characteristic: {sensor['characteristic']}")
                value = bytes(device.char_read(sensor['characteristic'])).decode('utf-8')
                values.append({'device': sensor['device'], 'value': value})
            else:	# Sends "SEND" to the device and waits for a notification to respond
                print(f"[INFO] Connecting to device: {sensor['device']}")
                device = adapter.connect(sensor['device'])
                print(f"[INFO] Sending wake up string...")
                device.char_write(sensor['characteristic'], bytearray([0x45]*80)) # Sends "E"*80 to wake it up
                time.sleep(2)
                print(f"[INFO] Sending: \"SEND\"...")
                device.char_write(sensor['characteristic'], bytearray([0x53, 0x45, 0x4e, 0x44])) # Sends "SEND" to the device
                time.sleep(2)
                try:
                    print("Subscribing...")
                    device.subscribe(sensor['characteristic'], callback=handle_data)
                    time.sleep(2)
                except Exception as e:
                    if (e != None or e != "None"): print("Exception:",e)
                values.append({'device': sensor['device'], 'value': notification})
                notification = ""
                connection_attempts = 4 # Stops trying to connect, because it succeeded
        except Exception as e:
            print(f"[ERROR] Could not connect to {sensor['device']}")
        finally:
            adapter.stop()
            connection_attempts += 1




print("[DEBUG] Retrieved values:", values)

print(f"[INFO] Sending data to {MQTT_TOPIC}")
MQTT.publish(MQTT_TOPIC, json.dumps(values))
time.sleep(1)

MQTT.disconnect()
