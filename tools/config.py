import json


class Config:
    name: str
    _config: object or None

    def __init__(self, name: str):
        self.name = name
        self._config = None
        self._load()

    def _path(self):
        return f'config/{self.name}.json'

    def _load(self):
        with open(self._path()) as file:
            config_raw = file.read()
            self._config = json.loads(config_raw)

    def _save(self):
        with open(self._path(), 'w') as file:
            config_raw = json.dumps(self._config)
            file.write(config_raw)

    def get(self, key: str):
        return self._config[key]

    def set(self, key: str, value: any):
        self._config[key] = value
        self._save()

    def delete(self, key: str):
        del self._config[key]
        self._save()
