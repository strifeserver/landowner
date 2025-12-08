# repositories/users_repository.py
from models.access_level import AccessLevel
from models.Setting import Setting
import json
from pprint import pprint


class SettingsRepository:
    @staticmethod
    def find_all(filters=None, search=None):
        data = Setting.index(filters=filters, search=search)
        return data

    @staticmethod
    def find_by_id(id):
        results = Setting.index(filters={"id": id})
        return results[0] if results else None



    @staticmethod
    def store(data):
        return Setting.store(**data)

    @staticmethod
    def update(id, data):
        return Setting.update(id, **data)

    @staticmethod
    def destroy(id):
        return Setting.destroy(id)
