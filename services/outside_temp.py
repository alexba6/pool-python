import time

from services.web_socket import WebSocketClient
from tools.config import Config
from tools.temperature import TemperatureSensor


class OutsideTemp:
    sensor: TemperatureSensor
    lastTemp: float
    lastTempTime: int
    config: Config
    ws_client: WebSocketClient

    def __init__(self, ws_client: WebSocketClient):
        self.sensor = TemperatureSensor()
        self.lastTemp = - 127
        self.lastTempTime = 0
        self.config = Config('outside-temp')
        self.ws_client = ws_client

    def loop(self):
        now_time = time.time()
        if now_time - self.lastTempTime > self.config.get('save_interval'):
            temp = self.sensor.read()
            self.lastTemp = temp
            self.lastTempTime = now_time
            print('Before send')
            self.ws_client.send('SENSOR', {
                'name': 'outside_temp',
                'value': temp
            })
            print('After send')

    def init(self):
        self.sensor.id = self.config.get('sensor_id')

