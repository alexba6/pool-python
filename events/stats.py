import time

from machine import Pin

from app import socket

pingLed = Pin(2, Pin.OUT)
pingLed.on()


@socket.on('PING')
def pong(req, res):
    pingLed.off()
    time.sleep_ms(5)
    pingLed.on()



