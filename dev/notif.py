import pygatt
import time
from binascii import hexlify

adapter = pygatt.backends.GATTToolBackend()
notif = ""
def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    global notif
    notif = bytes(value).decode('utf-8')
try:
    adapter.start()
    print("Connecting...")
    device = adapter.connect('64:69:4E:80:20:17')
    time.sleep(2)
    print("Sending: SEND")
    device.char_write("0000ffe1-0000-1000-8000-00805f9b34fb", bytearray([0x53, 0x45, 0x4e, 0x44])) #Sends "SEND" to the device
    time.sleep(2)
    print("Subscribing...")
    device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=handle_data)
    time.sleep(2)
    print("Data returned:", notif)
    print("Unsubscribing...")
    device.unsubscribe("0000ffe1-0000-1000-8000-00805f9b34fb", wait_for_response=False)
    time.sleep(2)
except Exception as e:
    if (e != None): print("Exception:",e)
finally:
    print("Adapter Stopped")
    adapter.stop()

print("HERE IS THE NOTIFIATION DATA:", notif)
