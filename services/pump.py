import time
from machine import Pin

from lib.ds1307 import DS1307
from models.temp_slot import TempSlot
from services.water_temp import WaterTemp
from tools.config import Config
from tools.time_convert import get_sec

AUTO = 'AUTO'
ON = 'ON'
OFF = 'OFF'
FREEZE = 'FREEZE'
IDLE = 'IDLE'
STARTING = 'STARTING'


class PumpService(Config):
    pin: Pin
    mode: str
    state: bool
    current_temp_slot: TempSlot or None
    current_temp_average: float
    switch_time: int
    manual_switch_time: int
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
        self.manual_switch_time = 0
        self.state = True
        self.switch(False)
        self.load_config()

    def init(self):
        self.mode = STARTING
        self.switch(True)

    def refresh_temp_slot(self):
        self.current_temp_slot = None
        json_temp_slots = self.config['temp_slots']
        json_temp_slots.sort(key=lambda ts: ts['temp'], reverse=True)
        for json_temp_slot in json_temp_slots:
            if self.current_temp_average > json_temp_slot['temp']:
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

    def change_mode(self, mode: str):
        assert mode in [ON, OFF, AUTO], Exception('Invalid mode')
        if self.mode != mode:
            if mode in [ON, OFF]:
                self.manual_switch_time = time.time()
            self.mode = mode

    def end_day(self):
        self.current_temp_average = self.water_temp.get_average()
        self.refresh_temp_slot()
        self.water_temp.clear()

    def loop(self):
        mode = self.mode
        if mode == AUTO:
            if self.current_temp_slot:
                now_rtc = self.ds.datetime()[4:7]
                now_sec = get_sec(now_rtc)
                for time_slot in self.current_temp_slot.time_slots:
                    if time_slot.enable and get_sec(time_slot.start) <= now_sec < get_sec(time_slot.end):
                        self.switch(True)
                        return
                self.switch(False)
            else:
                self.switch(True)
        elif mode == ON or mode == OFF:
            self.switch(mode == ON)
            now_time = time.time()
            if now_time - self.manual_switch_time > self.config.get('manual_max_time'):
                self.mode = AUTO
        elif mode == STARTING:
            now_time = time.time()
            if now_time - self.switch_time > self.config.get('starting_time'):
                self.current_temp_average = self.water_temp.get_average()
                self.refresh_temp_slot()
                self.mode = AUTO
