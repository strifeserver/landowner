# services/UsersService.py

from models.user import User
from services.BaseService import BaseService

class UsersService(BaseService):
    def __init__(self):
        super().__init__(User)

# Example usage:

# service = UsersService()

# service.index(filters={"status": "active"}, pagination=True, items_per_page=5, page=1)

# service.fetch_one(user_id)

# service.store(data)

# service.update(user_id, data)

# service.delete(user_id)
