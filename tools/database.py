import json
import re
import os

from tools.id import id_generator


class DatabaseException(Exception):
    error: str

    def __init__(self, error: str):
        super().__init__(error)
        self.error = error


class Repository:
    entity: type
    db_path_dir: str

    def __init__(self, db_path_dir: str, entity: type):
        self.db_path_dir = db_path_dir
        self.entity = entity
        if self._repository_file() not in os.listdir(self.db_path_dir):
            self.truncate()

    def _repository_file(self):
        class_name = self.entity().__class__.__name__
        return re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name).lower() + '.json'

    def _path(self):
        return f'{self.db_path_dir}/{self._repository_file()}'

    def _load(self) -> list:
        with open(self._path()) as file:
            raw_rows = file.read()
            return json.loads(raw_rows)

    def _save(self, rows: list):
        with open(self._path(), 'w') as file:
            raw_rows = json.dumps(rows)
            file.write(raw_rows)

    def find(self, key: str, value: any):
        rows = self._load()
        for row in rows:
            if row[key] == value:
                entity = self.entity()
                for key in row.keys():
                    setattr(entity, key, row[key])
                return entity
        return None

    def find_all(self, where=None):
        rows = self._load()
        items = []
        for row in rows:
            entity = self.entity()
            for key in row.keys():
                setattr(entity, key, row[key])
            if where:
                if not where(entity):
                    continue
            items.append(entity)
        return items

    def insert(self, entity: any):
        rows = self._load()
        entity.id = id_generator(5)
        rows.append(entity.__dict__)
        self._save(rows)

    def update(self, entity: any):
        rows = self._load()
        for index in range(len(rows)):
            if rows[index]['id'] == entity.id:
                rows[index] = entity.__dict__
                self._save(rows)
                return
        raise DatabaseException('ENTITY_NOT_FOUND')

    def delete(self, entity: any):
        rows = self._load()
        for index in range(len(rows)):
            if rows[index]['id'] == entity.id:
                rows.pop(index)
                self._save(rows)
                return
        raise DatabaseException('ENTITY_NOT_FOUND')

    def truncate(self):
        self._save([])


class Database:
    path_dir: str

    def __init__(self, path_dir: str):
        self.path_dir = path_dir
        if path_dir not in os.listdir():
            os.mkdir(path_dir)

    def get_repository(self, entity: type) -> Repository:
        return Repository(self.path_dir, entity)
