# repositories/users_repository.py
from models.access_level import AccessLevel
from models.user import User
import json
from pprint import pprint


class UsersRepository:
    @staticmethod
    def find_all(filters=None, search=None):
        users = User.index(filters=filters, search=search)
        users = UsersRepository.add_access_level_names(users)

        return users

    @staticmethod
    def find_by_id(user_id):
        results = User.index(filters={"id": user_id})
        results = UsersRepository.add_access_level_names(results)
        return results[0] if results else None

    @staticmethod
    def add_access_level_names(users):
        # If this is a dict coming from index(), extract the real list
        if isinstance(users, dict):
            users_list = users.get("data", [])
        else:
            users_list = users

        access_levels = {
            al.id: al.access_level_name
            for al in AccessLevel.index()
        }

        for user in users_list:
            level_id = int(getattr(user, "access_level", 0) or 0)
            setattr(user, "access_level_name", access_levels.get(level_id, "N/A"))

        return users_list


    @staticmethod
    def store(data):
        return User.store(**data)

    @staticmethod
    def update(id, data):
        return User.update(id, **data)

    @staticmethod
    def destroy(id):
        return User.destroy(id)
