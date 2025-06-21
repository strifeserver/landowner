# models/access_level.py
import os
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "data.db")

class AccessLevel(BaseModel):
    table_name = "access_levels"
    fields = ["id", "access_level_name"]

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1):
        return super().index_sqlite(
            DB_PATH,              # ✅ This is what was missing
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page
        )
