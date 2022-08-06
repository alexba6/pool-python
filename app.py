import machine

from lib.ds1307 import DS1307

import services.websocket
import services.wifi
import services.pump
import services.water_temp
import services.outside_temp

i2c = machine.I2C(
    sda=machine.Pin(21, mode=machine.Pin.OUT, pull=machine.Pin.PULL_UP),
    scl=machine.Pin(22, mode=machine.Pin.OUT, pull=machine.Pin.PULL_UP)
)

ds = DS1307(i2c)
socket = services.websocket.WebSocket()
water_temperature = services.water_temp.WaterTemp()
outside_temperature = services.outside_temp.OutsideTemp(ds)
pump = services.pump.PumpService(26, ds, water_temperature)
wifi = services.wifi.Wifi()
