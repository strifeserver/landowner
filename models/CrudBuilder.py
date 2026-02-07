# models/CrudBuilder.py
import os
import json
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class CrudBuilder(BaseModel):
    db_path = DB_PATH
    table_name = "crud_definitions"
    fields = ['id', 'name', 'table_name', 'fields_json', 'sort_field', 'sort_direction', 'created_at', 'updated_at']

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False},
        "name": {"alias": "Maintenance Name", "order": 1, "editable": True},
        "table_name": {"alias": "Table Name", "order": 2, "editable": False},
        "fields_json": {"alias": "Fields Config", "is_hidden": True, "editable": True},
        "sort_field": {"alias": "Default Sort", "order": 3, "editable": True},
        "sort_direction": {
            "alias": "Direction", 
            "order": 4, 
            "editable": True,
            "options": ["ASC", "DESC"]
        },
        "created_at": {"alias": "Created", "order": 5, "is_hidden": False, "editable": False},
        "updated_at": {"alias": "Updated", "order": 6, "is_hidden": True, "editable": False},
    }

    def __init__(self, **kwargs):
        for field in self.fields:
            if field in kwargs:
                setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1, **kwargs):
        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            sort_by=kwargs.get('sort_by', 'id'),
            sort_order=kwargs.get('sort_order', 'DESC')
        )

    @classmethod
    def edit(cls, id):
        return super().edit_sqlite(DB_PATH, cls.table_name, cls.fields, row_id=id)

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    @classmethod
    def update(cls, id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, id, **kwargs)

    @classmethod
    def destroy(cls, id):
        return super().destroy_sqlite(DB_PATH, cls.table_name, id)

    @classmethod
    def get_dynamic_field_definitions(cls):
        return cls.field_definitions
