from models.access_level import AccessLevel
from models.user import User
import json

class UsersRepository:

    @staticmethod
    def find_all(filters=None, search=None):
        users = User.index(filters=filters, search=search)
        users = UsersRepository.add_access_level_names(users)

        # 👇 DEBUG: Print users as JSON
        print(json.dumps([user.__dict__ for user in users], indent=4))

        return users

    @staticmethod
    def find_by_id(user_id):
        results = User.index(filters={"id": user_id})
        results = UsersRepository.add_access_level_names(results)
        return results[0] if results else None

    @staticmethod
    def add_access_level_names(users):
        access_levels = {al.id: al.access_level_name for al in AccessLevel.index()}

        for user in users:
            level_id = int(getattr(user, "access_level", 0) or 0)
            setattr(user, "access_level_name", access_levels.get(level_id, "N/A"))

        return users

    @staticmethod
    def store(data):
        return User.store(**data)
