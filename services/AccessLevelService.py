# services/AccessLevelService.py

from repositories.users_repository import UsersRepository
from models.access_level import AccessLevel
from services.BaseService import BaseService

class AccessLevelService(BaseService):
    def __init__(self):
        super().__init__(AccessLevel)

# Example usage:

# service = AccessLevelService()

# service.index(filters={"status": "active"}, pagination=True, items_per_page=5, page=1)

# service.fetch_one(user_id)

# service.store(data)

# service.update(user_id, data)

# service.delete(user_id)
