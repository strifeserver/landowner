# models/user.py
import os
from datetime import datetime
from models.base_model import BaseModel
from utils.debug import print_r
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db"
)


class AccessLevel(BaseModel):
    table_name = "access_levels"
    fields = ["id", "access_level_name", "access_level_code"]

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False},
        "access_level_name": {
            "alias": "Access Level Name",
            "is_hidden": False,
            "order": 2,
            "editable": True,
        },
        "access_level_code": {
            "alias": "Access Level Code",
            "is_hidden": False,
            "order": 2,
            "editable": True,
        },

    }

    # Only DB columns
    fields = [
        "id",
        "access_level_name",
        "access_level_code",
    ]

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

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
            prefix = f"{table_alias}." if table_alias else ""
            fields_to_select = [f"{prefix}{f}" for f in cls.fields]
            select_clause = ", ".join(fields_to_select)
            custom_query = f"SELECT {select_clause} FROM {cls.table_name} {table_alias or ''}"

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
    def get_dynamic_field_definitions(cls):
        """Injects access_level options dynamically based on AccessLevel.index()"""
        field_defs = dict(cls.field_definitions)

        try:
            access_levels = AccessLevel.index()
            field_defs["access_level_name"]["options"] = [
                {"label": al.access_level_name, "value": al.id} for al in access_levels
            ]
        except Exception as e:
            print("Failed to load access level options:", e)
            field_defs["access_level_name"]["options"] = []

        return field_defs
