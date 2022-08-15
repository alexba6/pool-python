import time

import math

from services.web_socket import WebSocketClient
from tools.config import Config
from tools.temperature import TemperatureSensor


class WaterTemp:
    sensor: TemperatureSensor
    temp_buffer: list
    lastTemp: float
    lastTempTime: int
    run: bool
    config: Config
    ws_client: WebSocketClient

    def __init__(self, ws_client: WebSocketClient):
        self.sensor = TemperatureSensor()
        self.lastTemp = - 127
        self.lastTempTime = 0
        self.temp_buffer = []
        self.run = False
        self.config = Config('water-temp')
        self.ws_client = ws_client

    def loop(self):
        if not self.run:
            return
        now_time = time.time()
        if now_time - self.lastTempTime > self.config.get('save_interval'):
            temp = self.sensor.read()
            self.lastTemp = temp
            self.lastTempTime = now_time
            self.temp_buffer.append(temp)
            if len(self.temp_buffer) > 100:
                self.temp_buffer.pop(0)
            self.ws_client.send('SENSOR', {
                'name': 'water_temp',
                'value': temp
            })

    def get_size(self):
        return len(self.temp_buffer)

    def get_average(self, decimal: int = 1):
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
