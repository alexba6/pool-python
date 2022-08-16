

class Clock:
    id: str
    slotId: str
    start: list
    end: list
    enable: bool

    def __init__(self):
        self.id = ''
        self.slotId = ''
        self.start = [0, 0, 0]
        self.end = [0, 0, 0]
        self.enable = True

    def format(self):
        return {
            'id': self.id,
            'slotId': self.slotId,
            'start': self.start,
            'end': self.end,
            'enable': self.enable
        }
