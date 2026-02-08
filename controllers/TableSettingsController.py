# controllers/TableSettingsController.py
from services.TableSettingsService import TableSettingsService
from models.table_setting import TableSetting

class TableSettingsController:
    model = TableSetting

    @staticmethod
    def index(filters=None, pagination=False, items_per_page=10, page=1, searchAll=None):
        service = TableSettingsService()
        return service.index(filters=filters or {}, pagination=pagination, items_per_page=items_per_page, page=page, search=searchAll)

    @staticmethod
    def edit(data):
        # data might be the integer ID or the record object/dict
        row_id = data
        if hasattr(data, "id"):
            row_id = data.id
        elif isinstance(data, dict):
            row_id = data.get("id")

        from views.table_settings.table_settings_detail_view import TableSettingsDetailView
        service = TableSettingsService()
        record = service.edit(row_id)
        if not record:
            return None
        return {
            "view_type": "custom",
            "view_class": TableSettingsDetailView,
            "initial_data": record
        }

    @staticmethod
    def update(id, data):
        service = TableSettingsService()
        return service.update(id, data)
