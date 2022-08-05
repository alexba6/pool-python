from models.time_slot import TimeSlot


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