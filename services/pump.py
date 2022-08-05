import time
from machine import Pin

from lib.ds1307 import DS1307
from services.water_temp import WaterTemp
from tools.config import Config

AUTO = 'AUTO'
ON = 'ON'
OFF = 'OFF'
FREEZE = 'FREEZE'
IDLE = 'IDLE'
STARTING = 'STARTING'


def get_sec(time_array):
    return time_array[0] * 3600 + time_array[1] * 60 + time_array[2]


class TimeSlot:
    start: list
    end: list
    enable: bool

    def __init__(self, time_slot_json: object or None = None):
        self.start = [0, 0, 0]
        self.end = [0, 0, 0]
        self.enable = True
        if time_slot_json:
            self.start = time_slot_json.get('start')
            self.end = time_slot_json.get('end')
            self.enable = time_slot_json.get('enable')

    def object(self):
        return {
            'start': self.start,
            'end': self.end,
            'enable': self.enable
        }


class TempSlot:
    temperature: float
    time_slots: list

    def __init__(self, temp_slot_json: object or None = None):
        self.temperature = 0
        self.time_slots = []
        if temp_slot_json:
            self.temperature = temp_slot_json.get('temp')
            self.time_slots = [TimeSlot(time_slot_json) for time_slot_json in temp_slot_json.get('time_slots')]

    def object(self):
        return {
            'temperature': self.temperature,
            'time_slots': [time_slot.object() for time_slot in self.time_slots]
        }


class PumpService(Config):
    pin: Pin
    mode: str
    state: bool
    current_temp_slot: TempSlot or None
    switch_time: int
    water_temp: WaterTemp
    ds: DS1307

    def __init__(self, pin: int, ds: DS1307, water_temp: WaterTemp):
        super().__init__('pump')
        self.pin = Pin(pin, Pin.OUT)
        self.mode = IDLE
        self.pin.on()
        self.current_temp_slot = None
        self.water_temp = water_temp
        self.ds = ds
        self.switch_time = 0
        self.state = True
        self.switch(False)
        self.load_config()

    def init(self):
        self.mode = STARTING
        self.switch(True)

    def load_temp_slot(self, temp: float):
        self.current_temp_slot = None
        json_temp_slots = self.config['temp_slots']
        json_temp_slots.sort(key=lambda ts: ts['temp'], reverse=True)
        for json_temp_slot in json_temp_slots:
            if temp > json_temp_slot['temp']:
                self.current_temp_slot = TempSlot(json_temp_slot)
                break

    def switch(self, state: bool):
        if self.state == state:
            return
        if state:
            self.pin.off()
        else:
            self.pin.on()
        self.water_temp.set_run(state)
        self.state = state
        self.switch_time = time.time()

    def loop(self):
        mode = self.mode
        if mode == AUTO:
            if self.current_temp_slot:
                now = self.ds.datetime()[4:7]
                now_sec = get_sec(now)
                for time_slot in self.current_temp_slot.time_slots:
                    if time_slot.enable and get_sec(time_slot.start) <= now_sec < get_sec(time_slot.end):
                        self.switch(True)
                        return
                self.switch(False)
            else:
                self.switch(True)
        elif mode == STARTING:
            now = time.time()
            if now - self.switch_time > self.config.get('starting_time'):
                temp = self.water_temp.get_average()
                self.load_temp_slot(temp)
                self.mode = AUTO
