#user.py
import os
from models.base_model import BaseModel
from models.access_level import AccessLevel
from utils.debug import print_r
from datetime import datetime
import json


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
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            

        results = []

        for record in data:
            # Global search
            if search:
                if any(search.lower() in str(value).lower() for value in record.values()):
                    results.append(cls(**record))
                continue

            # Advanced filters
            print_r('FILTERS')
            print_r(filters)
            if filters:
                match = True
                for key, value in filters.items():
                    match key:
                        case 'id':
                            try:
                                match = match and int(record.get('id', -1)) == int(value)
                            except ValueError:
                                match = False

                        case 'created_at_from':
                            try:
                                record_date = datetime.strptime(record.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                                from_date = datetime.strptime(value, '%Y-%m-%d')
                                match = match and record_date >= from_date
                            except ValueError:
                                match = False

                        case 'created_at_to':
                            try:
                                record_date = datetime.strptime(record.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                                to_date = datetime.strptime(value, '%Y-%m-%d')
                                match = match and record_date <= to_date
                            except ValueError:
                                match = False

                        case _:
                            match = match and str(record.get(key, '')).lower() == str(value).lower()

                if match:
                    results.append(cls(**record))
                continue

            results.append(cls(**record))

        if pagination:
            start = (page - 1) * items_per_page
            end = start + items_per_page
            results = results[start:end]

        # Add access level names
        access_levels = {
            getattr(al, "id"): getattr(al, "access_level_name")
            for al in AccessLevel.index()
        }

        for user in results:
            level_id = (
                int(getattr(user, "access_level", 0))
                if getattr(user, "access_level", None)
                else 0
            )
            setattr(user, "access_level_name", access_levels.get(level_id, "N/A"))

        return results

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
