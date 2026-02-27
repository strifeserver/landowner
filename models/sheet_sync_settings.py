# models/sheet_sync_settings.py
import os
from models.base_model import BaseModel
from models.db_config import DB_PATH


class SheetSyncSettings(BaseModel):
    table_name = "sheet_sync_settings"
    fields = [
        "id",
        "table_name",           # 'orders', 'payments', 'expenses'
        "settings_json",        # Stores column config: [{"name": "col", "sync": True, "order": 1}, ...]
        "created_at",
        "updated_at",
        "created_by",
        "updated_by"
    ]

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 1, "editable": False},
        "table_name": {"alias": "Table Name", "order": 2, "editable": False},
        "settings_json": {"alias": "Sync Config", "is_hidden": True, "order": 3, "editable": True},
        "created_at": {"alias": "Date Created", "order": 4, "editable": False},
        "updated_at": {"alias": "Date Updated", "order": 5, "editable": False},
        "created_by_name": {"alias": "Created By", "order": 6, "editable": False},
        "updated_by_name": {"alias": "Updated By", "order": 7, "editable": False}
    }

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    @classmethod
    def get_ambiguous_fields(cls):
        return ["id", "created_at", "updated_at", "created_by", "updated_by"]

    @classmethod
    def find_by_table(cls, table_name):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = f"SELECT * FROM {cls.table_name} WHERE table_name = ?"
        cursor.execute(query, (table_name,))
        row = cursor.fetchone()
        conn.close()
        return row

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    @classmethod
    def update(cls, row_id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, row_id, **kwargs)
