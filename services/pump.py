import time
from machine import Pin

from tools.database import Database, Repository
from tools.ds1307 import DS1307
from tools.config import Config
from tools.time_convert import get_sec

from models.slot import Slot

from services.water_temp import WaterTemp


AUTO = 'AUTO'
ON = 'ON'
OFF = 'OFF'
FREEZE = 'FREEZE'
IDLE = 'IDLE'
STARTING = 'STARTING'


class PumpService:
    pin: Pin
    mode: str
    state: bool
    current_slot: Slot or None
    current_temp_average: float
    switch_time: int
    manual_switch_time: int
    water_temp: WaterTemp
    ds: DS1307
    config: Config
    repo: Repository

    def __init__(self, pin: int, ds: DS1307, water_temp: WaterTemp, db: Database):
        self.pin = Pin(pin, Pin.OUT)
        self.mode = IDLE
        self.pin.on()
        self.current_slot = None
        self.water_temp = water_temp
        self.ds = ds
        self.switch_time = 0
        self.manual_switch_time = 0
        self.state = True
        self.config = Config('pump')
        self.repo = db.get_repository(Slot)
        self.switch(False)

    def init(self):
        self.mode = STARTING
        self.switch(True)

    def refresh_temp_slot(self):
        self.current_slot = None
        slots = self.repo.fin_all()
        slots.sort(key=lambda ts: ts.temperature, reverse=True)
        for index in range(len(slots)):
            slot: Slot = slots[index]
            if self.current_temp_average > slot.temperature:
                print(slot.__dict__)
                self.current_slot = slot
                break

    def switch(self, state: bool):
        if self.state == state:
            return
        if state:
            self.pin.on()
        else:
            self.pin.off()
        self.water_temp.set_run(state)
        self.state = state
        self.switch_time = time.time()

    def change_mode(self, mode: str):
        assert mode in [ON, OFF, AUTO], Exception('Invalid mode')
        assert self.mode in [ON, OFF, AUTO], Exception('Cannot change mode')
        if self.mode != mode:
            if mode in [ON, OFF]:
                self.manual_switch_time = time.time()
                self.switch(mode == ON)
            self.mode = mode

    def end_day(self):
        self.current_temp_average = self.water_temp.get_average()
        self.refresh_temp_slot()
        self.water_temp.clear()

    def loop(self):
        mode = self.mode
        if mode == AUTO:
            current_slot: Slot = self.current_slot
            if current_slot:
                now_rtc = self.ds.datetime()[4:7]
                now_sec = get_sec(now_rtc)
                for start, end, enable in current_slot.slots:
                    if enable and get_sec(start) <= now_sec < get_sec(end):
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
