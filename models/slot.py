
class Slot:
    id: str
    temperature: int

    def __init__(self):
        self.id = ''
        self.temperature = - 127

    def format(self):
        return {
            'id': self.id,
            'temperature': self.temperature
        }