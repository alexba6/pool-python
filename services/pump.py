import time
from machine import Pin

from services.web_socket import WebSocketClient
from tools.database import Database
from tools.ds1307 import DS1307
from tools.config import Config
from tools.time_convert import get_sec

from models.slot import Slot
from models.clock import Clock

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
    current_clocks: list or None
    current_temp_average: float
    switch_time: int
    manual_switch_time: int
    water_temp: WaterTemp
    ds: DS1307
    config: Config
    db: Database
    ws_client: WebSocketClient

    def __init__(self, pin: int, ds: DS1307, water_temp: WaterTemp, db: Database, ws_client: WebSocketClient):
        self.pin = Pin(pin, Pin.OUT)
        self.mode = IDLE
        self.pin.on()
        self.current_clocks = None
        self.water_temp = water_temp
        self.ds = ds
        self.switch_time = 0
        self.manual_switch_time = 0
        self.state = True
        self.config = Config('pump')
        self.db = db
        self.ws_client = ws_client
        self.switch(False)

    def init(self):
        self.mode = STARTING
        self.switch(True)

    def refresh_slot(self):
        if self.mode == STARTING:
            return
        print('Refreshing')
        slot_repo = self.db.get_repository(Slot)
        slots = slot_repo.find_all()
        print('slots', slots, 'temmp', self.current_temp_average)
        slots.sort(key=lambda s: s.temperature, reverse=True)
        for index in range(len(slots)):
            slot: Slot = slots[index]
            if self.current_temp_average > slot.temperature:
                print('Slot found', slot.id)
                clock_repo = self.db.get_repository(Clock)
                clocks = clock_repo.find_all(lambda clock: clock.slotId == slot.id)
                print('Clocks', clocks)
                self.current_clocks = clocks
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
        self.ws_client.send('PUMP#CHANGE_STATE', {
            'state': state
        })

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
        self.refresh_slot()
        self.water_temp.clear()

    def loop(self):
        mode = self.mode

        def change_auto():
            self.mode = AUTO
            self.ws_client.send('PUMP#CHANGE_MODE', {
                'mode': self.mode
            })

        if mode == AUTO:
            current_clocks: list = self.current_clocks
            if current_clocks:
                now_rtc = self.ds.datetime()[4:7]
                now_sec = get_sec(now_rtc)
                for index in range(len(current_clocks)):
                    clock: Clock = current_clocks[index]
                    if clock.enable and get_sec(clock.start) <= now_sec < get_sec(clock.end):
                        self.switch(True)
                        return
                self.switch(False)
            else:
                self.switch(True)
        elif mode == ON or mode == OFF:
            self.switch(mode == ON)
            now_time = time.time()
            if now_time - self.manual_switch_time > self.config.get('manual_max_time'):
                change_auto()
        elif mode == STARTING:
            now_time = time.time()
            if now_time - self.switch_time > self.config.get('starting_time'):
                self.current_temp_average = self.water_temp.get_average()
                change_auto()
                self.refresh_slot()
