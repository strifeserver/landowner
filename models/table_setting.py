# models/table_setting.py
import os
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

class TableSetting(BaseModel):
    table_name = "table_settings"
    fields = [
        "id",
        "table_name",
        "table_description",
        "settings_json",
        "items_per_page",
        "table_height",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by"
    ]

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 1, "editable": False},
        "table_name": {"alias": "Table Name", "order": 2, "editable": False},
        "table_description": {"alias": "Description", "order": 3, "editable": True},
        "settings_json": {"alias": "Column Config", "is_hidden": True, "order": 4, "editable": True},
        "items_per_page": {"alias": "Items Per Page", "order": 5, "editable": True},
        "table_height": {"alias": "Table Height", "order": 6, "editable": True},
        "created_at": {"alias": "Date Created", "order": 7, "editable": False},
        "updated_at": {"alias": "Date Updated", "order": 8, "editable": False},
        "created_by_name": {"alias": "Created By", "order": 9, "editable": False},
        "updated_by_name": {"alias": "Updated By", "order": 10, "editable": False}
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
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1, **kwargs):
        join_query = f"""
            SELECT t.*, 
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {cls.table_name} t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.updated_by = u2.id
        """
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]
        
        return super().index_sqlite(
            DB_PATH, cls.table_name, cls.fields,
            filters=filters, search=search, pagination=pagination,
            items_per_page=items_per_page, page=page,
            custom_query=join_query, custom_fields=custom_fields,
            table_alias="t", **kwargs
        )

    @classmethod
    def edit(cls, row_id):
        join_query = f"""
            SELECT t.*, 
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {cls.table_name} t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.updated_by = u2.id
        """
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]
        return super().edit_sqlite(
            DB_PATH, cls.table_name, cls.fields, row_id,
            custom_query=join_query, custom_fields=custom_fields,
            table_alias="t"
        )

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    @classmethod
    def update(cls, row_id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, row_id, **kwargs)

    @classmethod
    def fetch_by_table_name(cls, table_name):
        """Helper to get settings for a specific table."""
        items = cls.index(filters={"table_name": table_name})
        if items:
            # If it's a paginated result (dict), data is in 'data' key
            if isinstance(items, dict):
                return items['data'][0] if items['data'] else None
            return items[0]
        return None
