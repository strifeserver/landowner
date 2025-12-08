# controllers/users_controller.py
from models.user import User
# from ..requests.UserRequest import UserRequest
from request_objects.UserRequest import UserRequest
from services.UsersService import UsersService


class UsersController:
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        
        indexData = UsersService.get_users(
            filters=filters or {},
            pagination=True,
            items_per_page=items_per_page,
            page=page,
            search=searchAll,
        )
        
        return indexData

    @staticmethod
    def create():
        field_definitions = User.get_dynamic_field_definitions()
        return field_definitions

    @staticmethod
    def store(data):
        return UsersService.store_user(data)

    @staticmethod
    def edit(id):
        result = UsersService.get_user(id)
        return result

    @staticmethod
    def update(id, data):
        print("Users Controller Update")
        return UsersService.update_user(id, data)

    @staticmethod
    def destroy(id):
        print("Users Controller Delete")
        return UsersService.delete_user(id)
