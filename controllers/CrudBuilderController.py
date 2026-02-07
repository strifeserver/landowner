# controllers/CrudBuilderController.py
from models.CrudBuilder import CrudBuilder
from services.CrudBuilderService import CrudBuilderService

class CrudBuilderController:
    model = CrudBuilder
    
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=10, page=1, searchAll=None):
        service = CrudBuilderService()
        return service.index(
            filters=filters or {},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )

    @staticmethod
    def create():
        from views.crud_builder.crud_builder_form import CrudBuilderForm
        return {
            "view_type": "custom",
            "view_class": CrudBuilderForm,
            "initial_data": {}
        }

    @staticmethod
    def store(data):
        service = CrudBuilderService()
        result = service.generate_module(data)
        if result.get("success"):
            return {"success": True, "message": f"Module '{data.get('name')}' generated successfully"}
        else:
            return {"success": False, "message": result.get("message", "Failed to generate module")}

    @staticmethod
    def edit(data):
        from views.crud_builder.crud_builder_form import CrudBuilderForm
        return {
            "view_type": "custom",
            "view_class": CrudBuilderForm,
            "initial_data": data
        }

    @staticmethod
    def update(id, data):
        service = CrudBuilderService()
        result = service.update_module(id, data)
        if result.get("success"):
            return {"success": True, "message": f"Module '{data.get('name')}' updated and regenerated successfully"}
        else:
            return {"success": False, "message": result.get("message", "Failed to update module")}

    @staticmethod
    def destroy(id):
        service = CrudBuilderService()
        result = service.delete_module(id)
        return {"success": True, "message": "Module deleted successfully"} if result else {"success": False, "message": "Failed to delete module"}
