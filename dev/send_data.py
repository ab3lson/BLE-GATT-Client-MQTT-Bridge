#!/usr/bin/python3
import pygatt

#BLE VARIABLES
adapter = pygatt.backends.GATTToolBackend()
sensors = []
values = []
notification = ""

adapter.start()

device = adapter.connect('64:69:4E:80:20:17',address_type=pygatt.BLEAddressType.public)
characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
device.char_write(characteristic, bytearray([0x53, 0x45, 0x4e, 0x44])) #Sends "SEND" to the device

#check the characteristic
value = device.char_read(characteristic)
try:
	print("NEW Characteristic:", value.decode('utf-8'))
except:
	print(" NEW Characteristic:", value)
adapter.stop()
