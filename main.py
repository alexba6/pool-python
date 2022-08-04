import time
import ntptime
from machine import Pin

import services.websocket
import services.wifi
import services.pump


pingLed = Pin(2, Pin.OUT)
pingLed.on()
socket = services.websocket.WebSocket()
pump = services.pump.PumpService(12)
wifi = services.wifi.Wifi()


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


while True:
    wlan_status = wifi.wlan.status()
    if wlan_status == services.wifi.STAT_IDLE or wlan_status == 255:
        # Connect to Wi-Fi app
        try:
            wifi.connect_best()
            ntptime.settime()
        except Exception as e:
            print('wifi error', e)
    elif wlan_status == services.wifi.STAT_GOT_IP:
        socket_status = socket.status
        if socket_status == services.websocket.CLOSED or socket_status == services.websocket.IDLE:
            # Connect to home server
            socket.connect()
    socket.loop()
