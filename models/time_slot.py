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

