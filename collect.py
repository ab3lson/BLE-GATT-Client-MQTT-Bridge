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
    if ' ' in line:
        try:
            split = line.strip().split(' ')
            if (split[2] != None): sensors.append({'device': split[0], 'characteristic': split[1], 'notif': True})
            else: sensors.append({'device': split[0], 'characteristic': split[1], 'notif': False})
        except:
            print(f"[ERROR] Bad sensor formatting: {line.strip()}\nTry formatting like: MAC_ADDRESS CHAR_UUID [notif/char]")


print(f"Getting data from {len(sensors)} sensors!")
for sensor in sensors:
    try:
        adapter.start()
        if not sensor["notif"]:
            print(f"[INFO] Connecting to device: {sensor['device']}")
            device = adapter.connect(sensor['device'])
            print(f"[INFO] Reading characteristic: {sensor['characteristic']}")
            value = bytes(device.char_read(sensor['characteristic'])).decode('utf-8')
            values.append({'device': sensor['device'], 'value': value})
        else:
            print(f"[INFO] Connecting to device: {sensor['device']}")
            device = adapter.connect(sensor['device'])
            device.char_write(sensor['characteristic'], bytearray([0x53, 0x45, 0x4e, 0x44])) #Sends "SEND" to the device
            try:
                time.sleep(2)
                print("Subscribing...")
                device.subscribe(sensor['characteristic'], callback=handle_data)
                time.sleep(2)
            except Exception as e:
                if (e != None or e != "None"): print("Exception:",e)
            print("Stopping Adapter...")
            adapter.stop()
            values.append({'device': sensor['device'], 'value': notification})
            notification = ""
    except Exception as e:
        print(f"[ERROR] Could not connect to {sensor['device']}")
    finally:
        adapter.stop()





#print("Retrieved values:", values)

MQTT.publish("ble/test", json.dumps(values))
time.sleep(1)

MQTT.disconnect()
