import random


def id_generator(size=6, chars='123456789abcdef'):
    return ''.join(random.choice(chars) for _ in range(size))


class TimeSlot:
    start: list
    end: list
    enable: bool
    id: str

    def __init__(self, time_slot_json: object or None = None):
        if time_slot_json:
            self.start = time_slot_json.get('start')
            self.id = time_slot_json.get('start')
            self.end = time_slot_json.get('end')
            self.enable = time_slot_json.get('enable')
        else:
            self.start = [0, 0, 0]
            self.end = [0, 0, 0]
            self.enable = True
            self.id = id_generator(10)

    def object(self):
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'enable': self.enable
        }


class TempSlot:
    temperature: float
    time_slots: list
    id: str

    def __init__(self, temp_slot_json: object or None = None):
        if temp_slot_json:
            self.id = temp_slot_json.get('id')
            self.temperature = temp_slot_json.get('temp')
            self.time_slots = [TimeSlot(time_slot_json) for time_slot_json in temp_slot_json.get('time_slots')]
        else:
            self.temperature = 0
            self.time_slots = []
            self.id = id_generator(10)

    def object(self):
        return {
            'id': self.id,
            'temp': self.temperature,
            'time_slots': [time_slot.object() for time_slot in self.time_slots]
        }
