import json


class Config:
    config_name: str
    config: object or None

    def __init__(self, name: str):
        self.config_name = name
        self.config = None

    def config_path(self):
        return f'config/{self.config_name}.json'

    def load_config(self):
        with open(self.config_path()) as file:
            config_raw = file.read()
            self.config = json.loads(config_raw)

    def save_config(self):
        with open(self.config_path(), 'w') as file:
            config_raw = json.dumps(self.config)
            file.write(config_raw)
