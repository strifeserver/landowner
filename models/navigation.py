import os
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class Navigation(BaseModel):
    table_name = "navigations"
    fields = ['id', 'menu_name', 'navigation', 'controller', 'navigation_type', 'navigation_order', 'parent_id', 'icon', 'tooltip', 'is_hidden', 'status', 'created_at', 'updated_at']

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1):
        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page
        )
