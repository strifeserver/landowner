# controllers/users_controller.py
from models.user import User
from requests.user_request import UserRequest
from services.users_service import UsersService

class UsersController:
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        return UsersService.get_users(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll,
        )

    @staticmethod
    def create():
        field_definitions = User.field_definitions
        return field_definitions
        
    @staticmethod
    def store(data):
        return UsersService.store_user(data)
    
    @staticmethod
    def edit(id):
        result = UsersService.get_user(id)
        print(result)
        return result
        
    
    @staticmethod
    def update(id, data):
        print('Users Controller Update')
        
    @staticmethod
    def destroy(id):
        print('Users Controller Delete')
        print('Destroy')