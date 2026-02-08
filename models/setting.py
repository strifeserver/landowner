import os
from datetime import datetime
from models.base_model import BaseModel
from utils.debug import print_r
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db"
)

class Setting(BaseModel):
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')
    table_name = "settings"
    fields = ['id', 'setting_name', 'setting_value', 'setting_options', 'created_at', 'updated_at', 'created_by', 'updated_by']

    # Add field_definitions to work with BaseService
    field_definitions = {
        "id": {},
        "setting_name": {"capitalize1st": False},
        "setting_value": {},
        "setting_options": {
                "is_hidden": True,
            },
        "created_at": {},
        "updated_at": {},
        "created_by_name": {"alias": "Created By", "editable": False},
        "updated_by_name": {"alias": "Updated By", "editable": False},
    }

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    @classmethod
    def index(
        cls,
        filters=None,
        search=None,
        pagination=False,
        items_per_page=10,
        page=1,
        custom_query=None,       # optional custom SQL
        custom_fields=None,      # optional, matches SELECT columns
        table_alias=None,        # optional alias for table in query
        debug=False,
    ):
        """
        Generic index method.
        - Works with or without joins.
        - custom_query overrides default SELECT.
        - custom_fields required if using custom_query.
        """
        # Default SELECT query if no custom_query
        if not custom_query:
            table_alias = table_alias or "t"
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

        if not custom_fields:
            custom_fields = cls.fields

        # Call lower-level method (index_sqlite) with everything
        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            custom_query=custom_query,
            custom_fields=custom_fields,
            table_alias=table_alias,
            debug=debug,
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
        """Standard method for returning field metadata."""
        return cls.field_definitions
