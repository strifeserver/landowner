import os
from models.base_model import BaseModel

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'navigations.json')

class Navigation(BaseModel):
    fields = ['id', 'menu_name', 'navigation','controller']

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))


    @classmethod
    def index(cls, **kwargs):
        return super().index(DATA_FILE, **kwargs)

    def __repr__(self):
        return f"<User id={self.id} menu_name={self.menu_name}>"


