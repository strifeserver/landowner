#user.py
import os
from models.base_model import BaseModel
from models.access_level import AccessLevel
from utils.debug import print_r

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "users.json"
)


class User(BaseModel):
    # Field configuration with alias, visibility, and display order
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
            "alias": "Access Level Name",
            "is_hidden": False,
            "order": 9,
        },
        "created_at": {"alias": "Date Created", "is_hidden": False, "order": 10},
        "updated_at": {"alias": "Date Updated", "is_hidden": False, "order": 11},
    }

    # Set the fields dynamically from field_definitions
    fields = list(field_definitions.keys())

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, **kwargs):
        users = super().index(DATA_FILE, **kwargs)
        access_levels = {
            getattr(al, "id"): getattr(al, "access_level_name")
            for al in AccessLevel.index()
        }
        # Example: {1: 'Administrator', 2: 'Staff', 3: 'Tenant'}

        for user in users:
            level_id = (
                int(getattr(user, "access_level", 0))
                if getattr(user, "access_level", None)
                else 0
            )
            setattr(user, "access_level_name", access_levels.get(level_id, "N/A"))

        return users

    @classmethod
    def store(cls, **kwargs):
        return super().store(DATA_FILE, **kwargs)

    @classmethod
    def get_visible_fields(cls):
        """Returns a list of (field_name, alias) for visible fields in order."""
        return sorted(
            [
                (key, val["alias"])
                for key, val in cls.field_definitions.items()
                if not val.get("is_hidden")
            ],
            key=lambda x: cls.field_definitions[x[0]].get("order", 999),
        )

    # Optional: for debugging or table header generation
    @classmethod
    def get_ordered_field_keys(cls):
        """Return just the field names (keys) in visible order"""
        return [key for key, _ in cls.get_visible_fields()]
