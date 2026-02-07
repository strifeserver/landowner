# controllers/NavigationsController.py
from models.navigation import Navigation
from services.NavigationsService import NavigationsService

class NavigationsController:
    
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=5, page=1, searchAll=None):
        service = NavigationsService()
        return service.index(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )

    @staticmethod
    def create():
        return {
            "view_type": "generic",
            "field_definitions": Navigation.get_dynamic_field_definitions()
        }

    @staticmethod
    def store(data):
        from app_requests.NavigationsRequest import NavigationsRequest
        request = NavigationsRequest(data, action="store")
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        service = NavigationsService()        
        result = service.store(request.get_validated_data())
        return {"success": True, "message": "Navigation created successfully"} if result else {"success": False, "message": "Failed to create navigation"}

    @staticmethod
    def edit(data):
        return {
            "view_type": "generic",
            "field_definitions": Navigation.get_dynamic_field_definitions(),
            "initial_data": data
        }

    @staticmethod
    def update(id, data):
        from app_requests.NavigationsRequest import NavigationsRequest
        request = NavigationsRequest(data, action="update")
        validation = request.validate()

        if validation is not True:
            return {"success": False, "errors": validation}

        service = NavigationsService()   
        result = service.update(id, request.get_validated_data())
        return {"success": True, "message": "Navigation updated successfully"} if result else {"success": False, "message": "Failed to update navigation"}

    @staticmethod
    def destroy(id):
        service = NavigationsService()   
        result = service.delete(id)
        return {"success": True, "message": "Navigation deleted successfully"} if result else {"success": False, "message": "Failed to delete navigation"}

    @staticmethod
    def move_up(id):
        """Move navigation item up (increase order)"""
        result = Navigation.move_up(id)
        return {"success": True, "message": "Navigation moved up"} if result else {"success": False, "message": "Failed to move navigation"}

    @staticmethod
    def move_down(id):
        """Move navigation item down (decrease order)"""
        result = Navigation.move_down(id)
        return {"success": True, "message": "Navigation moved down"} if result else {"success": False, "message": "Failed to move navigation"}
