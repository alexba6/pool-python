import time
from machine import Pin

import services.websocket
import services.wifi
import services.pump

from app import socket, pump, wifi, water_temperature
import tools.temperature

pingLed = Pin(2, Pin.OUT)
pingLed.on()


@socket.on('PING')
def pong(data, id):
    pingLed.off()
    time.sleep_ms(10)
    pingLed.on()


@socket.on('POST#STATE')
def post_state(data, callback):
    state = data['output']['state']
    pump.switch(services.pump.ON if state else services.pump.OFF)
    callback({
        'status': 'OK',
        'data': {
            'state': state
        }
    })


water_temperature.init()
pump.init()

while True:
    wlan_status = wifi.wlan.status()
    if wlan_status == services.wifi.STAT_IDLE or wlan_status == 255:
        # Connect to Wi-Fi app
        try:
            wifi.connect_best()
        except Exception as e:
            print('wifi error', e)
    elif wlan_status == services.wifi.STAT_GOT_IP:
        socket_status = socket.status
        if socket_status == services.websocket.CLOSED or socket_status == services.websocket.IDLE:
            # Connect to home server
            socket.connect()
    socket.loop()
    try:
        pump.loop()
    except Exception as e:
        print(e)
    try:
        water_temperature.loop()
    except Exception as e:
        print(e)
    try:
        tools.temperature.refresh_temperature()
    except Exception as e:
        print(e)
    print(water_temperature.temp_buffer)
    time.sleep_ms(100)
