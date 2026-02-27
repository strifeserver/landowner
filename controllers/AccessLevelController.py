# controllers/AccessLevelController.py
from models.access_level import AccessLevel
from services.AccessLevelService import AccessLevelService


class AccessLevelController:
    model = AccessLevel
    
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
        from views.access_level.access_level_form import AccessLevelForm
        return {
            "view_type": "custom",
            "view_class": AccessLevelForm
        }

    @staticmethod
    def store(data):
        service = AccessLevelService()        
        result = service.store(data)
        
        if result:
             # Refresh permissions if successful
            from utils.session import Session
            Session.notify_permission_change()
            return {"success": True, "message": "Access Level created successfully"}
            
        return {"success": False, "message": "Failed to create access level"}

    @staticmethod
    def edit(data):
        from views.access_level.access_level_form import AccessLevelForm
        # 'data' here is the row object (which has the id)
        return {
            "view_type": "custom",
            "view_class": AccessLevelForm,
            "initial_data": data
        }

    @staticmethod
    def update(id, data):
        service = AccessLevelService()   

        result = service.update(id, data)
        
        if result:
             # Refresh permissions if successful
            from utils.session import Session
            Session.notify_permission_change()
            return {"success": True, "message": "Access Level updated successfully"}
            
        return {"success": False, "message": "Failed to update access level"}

    @staticmethod
    def destroy(id):
        service = AccessLevelService()   

        result = service.delete(id)
        return {"success": True, "message": "Access Level deleted successfully"} if result else {"success": False, "message": "Failed to delete access level"}
