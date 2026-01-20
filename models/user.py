# models/user.py
import os
from models.base_model import BaseModel
from models.access_level import AccessLevel
from utils.debug import print_r

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db"
)


class User(BaseModel):
    table_name = "users"

    # -----------------------
    # Field Definitions (UI / metadata)
    # -----------------------
    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False},
        "customId": {"alias": "Employee ID", "order": 1, "editable": True},
        "username": {"alias": "Username", "order": 2, "editable": True},
        "password": {"alias": "Password", "is_hidden": True},
        "email": {"alias": "Email", "order": 4, "editable": True},
        "access_level": {
            "alias": "Access Level",
            "is_hidden": True,
            "editable": True,
            "options": [],
        },
        "account_status": {
            "alias": "Account Status",
            "order": 6,
            "options": ["active", "inactive", "pending"],
            "capitalize1st": True,
        },
        "is_locked": {
            "alias": "Is Locked",
            "order": 7,
            "options": [
                {"label": "True", "value": 1},
                {"label": "False", "value": 0}
            ],
            "subtitute_table_values": [
                {"label": "True", "value": 1},
                {"label": "False", "value": 0},
            ],
        },
        "temporary_password": {"alias": "Temporary Password", "is_hidden": True},
        "access_level_name": {
            "alias": "Access Level",
            "order": 9,
            "origin_field": "access_level",
        },
        "created_at": {"alias": "Date Created", "order": 10},
        "updated_at": {"alias": "Date Updated", "order": 11},
    }

    # -----------------------
    # Actual DB columns (users table)
    # -----------------------
    fields = [
        "id",
        "customId",
        "username",
        "password",
        "email",
        "access_level",
        "account_status",
        "is_locked",
        "temporary_password",
        "created_at",
        "updated_at",
    ]

    # -----------------------
    # Constructor
    # -----------------------
    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        # Joined field
        self.access_level_name = kwargs.get("access_level_name")

    # -----------------------
    # CRUD wrappers
    # -----------------------
    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)


    # -----------------------
    # GET single user (for edit)
    # -----------------------
    @classmethod
    def edit(cls, id=None, filters=None, debug=False):
        """
        Fetch a single user row.

        Args:
            id (int | str | User object): fetch by user id or object
            filters (dict): fetch by custom field(s)
            debug (bool): show SQL debug
        Returns:
            User instance or None
        """
        # -----------------------
        # If id is a User object, extract its id
        # -----------------------
        if id and not isinstance(id, (int, str)):
            try:
                id = id.id
            except AttributeError:
                raise ValueError("Invalid object passed as id — missing 'id' attribute")

        # Default: fetch by id if provided
        if id is not None:
            filters = {"id": id}

        # -----------------------
        # Use join query to include access_level_name
        # -----------------------
        user_fields = [f"u.{field}" for field in cls.fields]
        join_query = f"""
            SELECT
                {', '.join(user_fields)},
                a.access_level_name AS access_level_name
            FROM {cls.table_name} u
            LEFT JOIN access_levels a
                ON u.access_level = a.id
        """
        custom_fields = cls.fields + ["access_level_name"]

        return super().edit_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            custom_query=join_query,
            custom_fields=custom_fields,
            table_alias="u",
            debug=debug,
        )


    @classmethod
    def update(cls, id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, id, **kwargs)

    @classmethod
    def destroy(cls, id):
        return super().destroy_sqlite(DB_PATH, cls.table_name, id)

    # -----------------------
    # INDEX (with JOIN)
    # -----------------------
    @classmethod
    def index(
        cls,
        filters=None,
        search=None,
        pagination=False,
        items_per_page=10,
        page=1,
        debug=False,
    ):
        # Explicitly prefix user fields to avoid ambiguity
        user_fields = [f"u.{field}" for field in cls.fields]

        join_query = f"""
            SELECT
                {', '.join(user_fields)},
                a.access_level_name AS access_level_name
            FROM {cls.table_name} u
            LEFT JOIN access_levels a
                ON u.access_level = a.id
        """

        # Map SELECT columns → object attributes
        custom_fields = cls.fields + ["access_level_name"]

        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            custom_query=join_query,
            custom_fields=custom_fields,
            table_alias="u",   # ✅ important
            debug=debug,
        )

    @classmethod
    def get_next_custom_id(cls):
        """
        Auto-generates the next customId (Employee ID) by incrementing the current max.
        Example: 000021 -> 000022
        """
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"SELECT customId FROM {cls.table_name} ORDER BY CAST(customId AS INTEGER) DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()

            if row and row[0]:
                next_id = int(row[0]) + 1
            else:
                next_id = 1
                
            return f"{next_id:06}"
        except Exception as e:
            print(f"Error generating customId: {e}")
            return "000001"

    # -----------------------
    # Dynamic select options
    # -----------------------
    @classmethod
    def get_dynamic_field_definitions(cls):
        field_defs = dict(cls.field_definitions)

        try:
            access_levels = AccessLevel.index()
            field_defs["access_level"]["options"] = [
                {"label": al.access_level_name, "value": al.id}
                for al in access_levels
            ]
        except Exception:
            field_defs["access_level"]["options"] = []

        return field_defs
