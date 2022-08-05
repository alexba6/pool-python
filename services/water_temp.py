import time

import math

from tools.config import Config
from tools.temperature import TemperatureSensor


class WaterTemp(Config):
    sensor: TemperatureSensor
    temp_buffer: list
    lastTemp: float
    lastTempTime: int
    run: bool

    def __init__(self):
        super().__init__('water-temp')
        self.sensor = TemperatureSensor()
        self.lastTemp = - 127
        self.lastTempTime = 0
        self.temp_buffer = []
        self.run = False
        self.load_config()

    def loop(self):
        if not self.run:
            return
        now_time = time.time()
        if now_time - self.lastTempTime > self.config.get('save_interval'):
            temp = self.sensor.read()
            self.lastTemp = temp
            self.lastTempTime = now_time
            self.temp_buffer.append(temp)

    def get_size(self):
        return len(self.temp_buffer)

    def get_average(self, decimal: int = 2):
        if len(self.temp_buffer) == 0:
            return - 127
        temp_sum = 0
        for temp in self.temp_buffer:
            temp_sum += temp
        return math.ceil(10 ** decimal * temp_sum / self.get_size()) / 10 ** decimal

    def clear(self):
        self.temp_buffer = []

    def init(self):
        self.sensor.id = self.config.get('sensor_id')

    def set_run(self, run: bool):
        if run:
            self.lastTempTime = time.time()
        self.run = run
