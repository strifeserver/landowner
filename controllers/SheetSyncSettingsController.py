# controllers/SheetSyncSettingsController.py
from models.sheet_sync_settings import SheetSyncSettings
import json

class SheetSyncSettingsController:
    @staticmethod
    def get_settings(table_name):
        record = SheetSyncSettings.find_by_table(table_name)
        if record and record[2]:
            return json.loads(record[2])
        return []

    @staticmethod
    def save_settings(table_name, settings_list):
        # Check if exists
        existing = SheetSyncSettings.find_by_table(table_name)
        
        json_data = json.dumps(settings_list)
        
        if existing:
            SheetSyncSettings.update(existing[0], settings_json=json_data)
        else:
            SheetSyncSettings.store(
                table_name=table_name,
                settings_json=json_data
            )
        return True
