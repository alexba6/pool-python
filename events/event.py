import time

from machine import Pin

import services.pump

from app import socket, pump

pingLed = Pin(2, Pin.OUT)
pingLed.on()


@socket.on('PING')
def pong(data, id):
    pingLed.off()
    time.sleep_ms(5)
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
