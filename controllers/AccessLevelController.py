# controllers/AccessLevelController.py
from models.access_level import AccessLevel
# from ..requests.UserRequest import UserRequest
from request_objects.UserRequest import UserRequest
from services.AccessLevelService import AccessLevelService


class AccessLevelController:
    
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        
        service = AccessLevelService()

        indexData = service.index(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )
        
        return indexData

    @staticmethod
    def create():
        field_definitions = User.get_dynamic_field_definitions()
        return field_definitions

    @staticmethod
    def store(data):
        service = AccessLevelService()        
        return service.store_user(data)

    @staticmethod
    def edit(id):
        service = AccessLevelService()     
        result = service.get_user(id)
        return result

    @staticmethod
    def update(id, data):
        service = AccessLevelService()   
        print("Users Controller Update")
        return service.update_user(id, data)

    @staticmethod
    def destroy(id):
        service = AccessLevelService()   
        print("Users Controller Delete")
        return service.delete_user(id)
