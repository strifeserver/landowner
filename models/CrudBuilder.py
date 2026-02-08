# models/CrudBuilder.py
import os
import json
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class CrudBuilder(BaseModel):
    db_path = DB_PATH
    table_name = "crud_definitions"
    fields = ['id', 'name', 'table_name', 'fields_json', 'sort_field', 'sort_direction', 'created_at', 'updated_at', 'created_by', 'updated_by']

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
        "created_by_name": {"alias": "Created By", "order": 7, "editable": False},
        "updated_by_name": {"alias": "Updated By", "order": 8, "editable": False},
    }

    def __init__(self, **kwargs):
        for field in self.fields:
            if field in kwargs:
                setattr(self, field, kwargs.get(field))
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1, **kwargs):
        
        # Default SELECT query if no custom_query
        if not kwargs.get('custom_query'):
            table_alias = kwargs.get('table_alias', 't')
            prefix = f"{table_alias}."
            fields_to_select = [f'{prefix}"{f}"' for f in cls.fields]
            select_clause = ", ".join(fields_to_select)
            
            kwargs['custom_query'] = f"""
                SELECT {select_clause},
                       COALESCE(u1.name, u1.username) as created_by_name,
                       COALESCE(u2.name, u2.username) as updated_by_name
                FROM {cls.table_name} {table_alias}
                LEFT JOIN users u1 ON {table_alias}.created_by = u1.id
                LEFT JOIN users u2 ON {table_alias}.updated_by = u2.id
            """
            kwargs['custom_fields'] = cls.fields + ["created_by_name", "updated_by_name"]
            kwargs['table_alias'] = table_alias

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
            sort_order=kwargs.get('sort_order', 'DESC'),
            custom_query=kwargs.get('custom_query'),
            custom_fields=kwargs.get('custom_fields'),
            table_alias=kwargs.get('table_alias')
        )

    @classmethod
    def edit(cls, id, **kwargs):
        table_alias = "t"
        prefix = f"{table_alias}."
        fields_to_select = [f'{prefix}"{f}"' for f in cls.fields]
        select_clause = ", ".join(fields_to_select)
        
        custom_query = f"""
            SELECT {select_clause},
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {cls.table_name} {table_alias}
            LEFT JOIN users u1 ON {table_alias}.created_by = u1.id
            LEFT JOIN users u2 ON {table_alias}.updated_by = u2.id
        """
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]
        
        return super().edit_sqlite(
            DB_PATH, 
            cls.table_name, 
            cls.fields, 
            row_id=id, 
            custom_query=custom_query, 
            custom_fields=custom_fields,
            table_alias=table_alias
        )

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
