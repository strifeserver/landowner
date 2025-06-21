import os
from models.base_model import BaseModel

class Setting(BaseModel):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')
    table_name = "settings"
    fields = ['id', 'setting_name', 'setting_value', 'setting_options', 'created_at', 'updated_at']

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1):
        return super().index_sqlite(
            cls.db_path,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page
        )

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(cls.db_path, cls.table_name, **kwargs)
