import machine

from tools.database import Database
from tools.ds1307 import DS1307

import services.web_socket
import services.wifi
import services.pump
import services.water_temp
import services.outside_temp

i2c = machine.I2C(
    sda=machine.Pin(21, mode=machine.Pin.OUT, pull=machine.Pin.PULL_UP),
    scl=machine.Pin(22, mode=machine.Pin.OUT, pull=machine.Pin.PULL_UP)
)

db = Database('database')
ds = DS1307(i2c)
ws_client = services.web_socket.WebSocketClient()
water_temperature = services.water_temp.WaterTemp(ws_client)
outside_temperature = services.outside_temp.OutsideTemp(ws_client)
pump = services.pump.PumpService(26, ds, water_temperature, db, ws_client)
wifi = services.wifi.Wifi(db)
