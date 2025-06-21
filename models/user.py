import os
from datetime import datetime
from models.base_model import BaseModel
from models.access_level import AccessLevel  # <-- make sure this import exists

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db"
)


class User(BaseModel):
    table_name = "users"

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False},
        "customId": {
            "alias": "Employee ID",
            "is_hidden": False,
            "order": 1,
            "editable": True,
        },
        "username": {
            "alias": "Username",
            "is_hidden": False,
            "order": 2,
            "editable": True,
        },
        "password": {"alias": "Password", "is_hidden": True, "order": 3},
        "email": {"alias": "Email", "is_hidden": False, "order": 4, "editable": True},
        "access_level": {
            "alias": "Access Level",
            "is_hidden": True,
            "order": 5,
            "editable": True,
            "options": [],  # Will be populated dynamically
        },
        "account_status": {
            "alias": "Account Status",
            "is_hidden": False,
            "order": 6,
            "options": ["active", "inactive", "pending"],
            "editable": True,
        },
        "is_locked": {
            "alias": "Locked",
            "is_hidden": False,
            "order": 7,
            "options": [True, False],
            "editable": True,
        },
        "temporary_password": {
            "alias": "Temporary Password",
            "is_hidden": True,
            "order": 8,
        },
        "access_level_name": {
            "alias": "Access Level",
            "is_hidden": False,
            "order": 9,
            "origin_field": "access_level",
        },
        "created_at": {"alias": "Date Created", "is_hidden": False, "order": 10},
        "updated_at": {"alias": "Date Updated", "is_hidden": False, "order": 11},
    }

    # Only DB columns
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

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    @classmethod
    def index(
        cls, filters=None, search=None, pagination=False, items_per_page=10, page=1
    ):
        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters,
            search,
            pagination,
            items_per_page,
            page,
        )

    @classmethod
    def get_visible_fields(cls):
        return sorted(
            [
                (key, val["alias"])
                for key, val in cls.field_definitions.items()
                if not val.get("is_hidden")
            ],
            key=lambda x: cls.field_definitions[x[0]].get("order", 999),
        )

    @classmethod
    def get_ordered_field_keys(cls):
        return [key for key, _ in cls.get_visible_fields()]

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
