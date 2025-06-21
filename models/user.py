# models/user.py

import os
import sqlite3
from datetime import datetime
from models.base_model import BaseModel

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db"
)


class User(BaseModel):
    table_name = "users"

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0},
        "customId": {"alias": "Employee ID", "is_hidden": False, "order": 1},
        "username": {"alias": "Username", "is_hidden": False, "order": 2},
        "password": {"alias": "Password", "is_hidden": True, "order": 3},
        "email": {"alias": "Email", "is_hidden": False, "order": 4},
        "access_level": {"alias": "Access Level", "is_hidden": True, "order": 5},
        "account_status": {"alias": "Account Status", "is_hidden": False, "order": 6},
        "is_locked": {"alias": "Locked", "is_hidden": False, "order": 7},
        "temporary_password": {
            "alias": "Temporary Password",
            "is_hidden": True,
            "order": 8,
        },
        "access_level_name": {
            "alias": "Access Level",
            "is_hidden": False,
            "order": 9,
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
