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
        "view": {"alias": "View", "is_hidden": True, "order": 3, "editable": False},
        "add": {"alias": "Add", "is_hidden": True, "order": 4, "editable": False},
        "edit": {"alias": "Edit", "is_hidden": True, "order": 5, "editable": False},
        "delete": {"alias": "Delete", "is_hidden": True, "order": 6, "editable": False},
        "export": {"alias": "Export", "is_hidden": True, "order": 7, "editable": False},
        "import": {"alias": "Import", "is_hidden": True, "order": 8, "editable": False},
        "created_at": {"alias": "Date Created", "order": 9, "is_hidden": True},
        "updated_at": {"alias": "Date Updated", "order": 10, "is_hidden": True},
        "created_by_name": {"alias": "Created By", "order": 11, "editable": False},
        "updated_by_name": {"alias": "Updated By", "order": 12, "editable": False},
    }

    # Only DB columns
    fields = [
        "id",
        "access_level_name",
        "access_level_code",
        "view",
        "add",
        "edit",
        "delete",
        "export",
        "import",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        # Joined fields
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    def get_permissions_list(self, permission_type):
        """Returns a list of integer IDs from the CSV string of the given permission type."""
        if permission_type not in self.fields:
            return []
        
        val = getattr(self, permission_type, "")
        if not val:
            return []
            
        # Handle cases where val might be an int or none (though init sets it to "")
        if isinstance(val, int):
            return [val]
            
        return [int(x.strip()) for x in str(val).split(",") if x.strip().isdigit()]

    def set_permissions_list(self, permission_type, id_list):
        """Sets the CSV string for a permission type from a list of integer IDs."""
        if permission_type not in self.fields:
            return
            
        csv_str = ",".join(str(i) for i in id_list)
        setattr(self, permission_type, csv_str)


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
            prefix = f"{table_alias or 't'}."
            fields_to_select = [f'{prefix}"{f}"' for f in cls.fields]
            select_clause = ", ".join(fields_to_select)
            custom_query = f"""
                SELECT {select_clause},
                       COALESCE(u1.name, u1.username) as created_by_name,
                       COALESCE(u2.name, u2.username) as updated_by_name
                FROM {cls.table_name} {table_alias or 't'}
                LEFT JOIN users u1 ON {table_alias or 't'}.created_by = u1.id
                LEFT JOIN users u2 ON {table_alias or 't'}.updated_by = u2.id
            """
            custom_fields = cls.fields + ["created_by_name", "updated_by_name"]
            table_alias = table_alias or "t"

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
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    # -----------------------
    # GET single row (for edit)
    # -----------------------
    @classmethod
    def edit(cls, id=None, filters=None, debug=False, custom_query=None, custom_fields=None, table_alias=None):
        """
        Fetch a single row for editing.

        Args:
            id (int | str | object): fetch by id or object (object must have 'id' attribute)
            filters (dict): fetch by custom field(s)
            debug (bool): show SQL debug
            custom_query (str): optional custom SQL (e.g., with JOINs)
            custom_fields (list): fields for mapping when using custom_query
            table_alias (str): optional table alias for ambiguous fields

        Returns:
            Model instance or None
        """
        # -----------------------
        # If id is an object, extract its id
        # -----------------------
        if id and not isinstance(id, (int, str)):
            try:
                id = id.id
            except AttributeError:
                raise ValueError("Invalid object passed as id — missing 'id' attribute")

        # Default: fetch by id if provided
        if id is not None:
            filters = {"id": id}

        # If no custom query, just select all fields
        if not custom_query:
            table_alias = table_alias or "t"
            prefix = f"{table_alias}."
            quoted_fields = [f'{prefix}"{f}"' for f in cls.fields]
            custom_query = f"""
                SELECT {', '.join(quoted_fields)},
                       COALESCE(u1.name, u1.username) as created_by_name,
                       COALESCE(u2.name, u2.username) as updated_by_name
                FROM {cls.table_name} {table_alias}
                LEFT JOIN users u1 ON {table_alias}.created_by = u1.id
                LEFT JOIN users u2 ON {table_alias}.updated_by = u2.id
            """
            final_fields = cls.fields + ["created_by_name", "updated_by_name"]
        else:
            final_fields = custom_fields or cls.fields
            table_alias = table_alias or "t"

        # Call the base method
        return super().edit_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            custom_query=custom_query,
            custom_fields=final_fields,
            table_alias=table_alias,
            debug=debug,
        )



    @classmethod
    def update(cls, id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, id, **kwargs)

    @classmethod
    def destroy(cls, id):
        return super().destroy_sqlite(DB_PATH, cls.table_name, id)

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
