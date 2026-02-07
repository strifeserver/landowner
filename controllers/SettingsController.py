# controllers/SettingsController.py
from models.Setting import Setting
from services.SettingsService import SettingsService

class SettingsController:
    
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        service = SettingsService()
        # print("DEBUG SETTINGS FIELDS:", Setting.field_definitions)
        return service.index(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )

    @staticmethod
    def create():
        from models.Setting import Setting
        return {
            "view_type": "generic",
            "field_definitions": Setting.get_dynamic_field_definitions()
        }

    @staticmethod
    def store(data):
        from app_requests.SettingsRequest import SettingsRequest
        request = SettingsRequest(data, action="store")
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        service = SettingsService()        
        result = service.store(request.get_validated_data())
        return {"success": True, "message": "Setting created successfully"} if result else {"success": False, "message": "Failed to create setting"}

    @staticmethod
    def edit(data):
        # 'data' here is the Setting object passed from the table selection
        return {
            "view_type": "generic",
            "field_definitions": Setting.get_dynamic_field_definitions(),
            "initial_data": data
        }

    @staticmethod
    def update(id, data):
        from app_requests.SettingsRequest import SettingsRequest
        request = SettingsRequest(data, action="update")
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        service = SettingsService()   
        print("Settings Controller Update")
        result = service.update(id, request.get_validated_data())
        return {"success": True, "message": "Setting updated successfully"} if result else {"success": False, "message": "Failed to update setting"}

    @staticmethod
    def destroy(id):
        service = SettingsService()   
        print("Settings Controller Delete")
        result = service.delete(id)
        return {"success": True, "message": "Setting deleted successfully"} if result else {"success": False, "message": "Failed to delete setting"}
