# controllers/users_controller.py
from models.user import User
from requests.user_request import UserRequest

class UsersController:
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        return User.index(filters=filters or {}, pagination=pagination, items_per_page=items_per_page, page=page, search=searchAll)
