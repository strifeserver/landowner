# controllers/TableSettingsController.py
from services.TableSettingsService import TableSettingsService
from models.table_setting import TableSetting

class TableSettingsController:
    model = TableSetting

    @staticmethod
    def index(filters=None, pagination=False, items_per_page=10, page=1, searchAll=None):
        # System tables that should only be visible to admin users
        SYSTEM_TABLES = [
            'table_settings',
            'crud_definitions', 
            'access_levels',
            'settings',
            'navigations',
            'users'
        ]
        
        # Check if current user is admin
        from utils.session import Session
        user = Session.get_user()
        is_admin = False
        
        if user and hasattr(user, 'access_level_code'):
            is_admin = (user.access_level_code == 'admin')
        
        # If not admin, filter out system tables
        service = TableSettingsService()
        result = service.index(
            filters=filters or {}, 
            pagination=pagination, 
            items_per_page=items_per_page, 
            page=page, 
            search=searchAll
        )
        
        # Filter system tables if not admin
        if not is_admin:
            if isinstance(result, dict) and 'data' in result:
                # Paginated result
                result['data'] = [
                    item for item in result['data'] 
                    if getattr(item, 'table_name', None) not in SYSTEM_TABLES
                ]
                result['total_rows'] = len(result['data'])
            elif isinstance(result, list):
                # Non-paginated result
                result = [
                    item for item in result 
                    if getattr(item, 'table_name', None) not in SYSTEM_TABLES
                ]
        
        return result

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
        print(f"[DEBUG] TableSettingsController.update called with ID={id}")
        print(f"[DEBUG] Data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        if isinstance(data, dict) and 'settings_json' in data:
            print(f"[DEBUG] settings_json length: {len(data['settings_json'])} chars")
        
        service = TableSettingsService()
        result = service.update(id, data)
        print(f"[DEBUG] Update result: {result}")
        return result
