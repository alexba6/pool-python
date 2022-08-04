from machine import Pin

AUTO = 'AUTO'
ON = 'ON'
OFF = 'OFF'


class TimeSlot:
    start: tuple
    end: tuple
    enable: bool

    def __init__(self):
        self.start = (0, 0, 0)
        self.end = (0, 0, 0)
        self.enable = True

    def object(self):
        return {
            'start': self.start,
            'end': self.end,
            'enable': self.enable
        }


class TempSlot:
    temperature: float
    time_slots: list

    def __init__(self):
        self.temperature = 0
        self.enable = True
        self.time_slots = []

    def object(self):
        return {
            'temperature': self.temperature,
            'time_slots': [time_slot.object() for time_slot in self.time_slots]
        }


class PumpService:
    pin: Pin
    mode: str
    current_temp_slot: TempSlot or None

    def __init__(self, pin: int):
        self.pin = Pin(pin, Pin.OUT)
        self.mode = AUTO
        self.pin.on()
        self.current_temp_slot = None

    def switch(self, mode: str):
        if self.mode == mode:
            return
        if mode == ON:
            self.pin.off()
        elif mode == OFF:
            self.pin.on()
        self.mode = mode
