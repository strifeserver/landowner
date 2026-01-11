# controllers/users_controller.py
from models.access_level import AccessLevel
# from ..requests.UserRequest import UserRequest
from request_objects.UserRequest import UserRequest
from services.AccessLevelService import AccessLevelService
from utils.debug import print_r

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
        field_definitions = AccessLevel.get_dynamic_field_definitions()
        return field_definitions

    @staticmethod
    def store(data):
        service = AccessLevelService()        
        return service.store(data)

    @staticmethod
    def edit(id):
        service = AccessLevelService()     
        result = service.edit(id)
        return result

    @staticmethod
    def update(id, data):
        service = AccessLevelService()   
        print("Controller Update")
        return service.update(id, data)

    @staticmethod
    def destroy(id):
        service = AccessLevelService()   
        print("Controller Delete")
        return service.delete(id)
