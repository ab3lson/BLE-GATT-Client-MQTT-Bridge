#!/usr/bin/python3
import pygatt

#BLE VARIABLES
adapter = pygatt.backends.GATTToolBackend()
sensors = []
values = []
notification = ""

adapter.start()

device = adapter.connect('34:14:B5:92:49:B2',address_type=pygatt.BLEAddressType.public)
characteristic = "0000dfb1-0000-1000-8000-00805f9b34fb"
device.char_write(characteristic, bytearray([0x53, 0x45, 0x4e, 0x44])) #Sends "SEND" to the device

#check the characteristic
value = device.char_read(characteristic)

print("NEW Characteristic:", value.decode('utf-8'))
adapter.stop()
