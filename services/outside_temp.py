import time

import math

from tools.ds1307 import DS1307
from tools.config import Config
from tools.temperature import TemperatureSensor
from tools.time_convert import get_sec


class OutsideTemp:
    sensor: TemperatureSensor
    temp_buffer: list
    lastTemp: float
    lastTempTime: int
    ds: DS1307
    config: Config

    def __init__(self, ds: DS1307):
        self.sensor = TemperatureSensor()
        self.lastTemp = - 127
        self.lastTempTime = 0
        self.temp_buffer = []
        self.ds = ds
        self.config = Config('outside-temp')

    def loop(self):
        now_time = time.time()
        if now_time - self.lastTempTime > self.config.get('save_interval'):
            temp = self.sensor.read()
            self.lastTemp = temp
            self.lastTempTime = now_time
            now_dt = self.ds.datetime()[4:7]
            self.temp_buffer.append((temp, now_dt))
            if get_sec(now_dt) - get_sec(self.temp_buffer[0][1]) > self.config.get('max_save_time'):
                self.temp_buffer.pop(0)

    def get_size(self):
        return len(self.temp_buffer)

    def get_average(self, decimal: int = 2):
        if len(self.temp_buffer) == 0:
            return - 127
        temp_sum = 0
        for temp in self.temp_buffer:
            temp_sum += temp[0]
        return math.ceil(10 ** decimal * temp_sum / self.get_size()) / 10 ** decimal

    def init(self):
        self.sensor.id = self.config.get('sensor_id')

