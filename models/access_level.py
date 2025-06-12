import os
from models.base_model import BaseModel

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "access_levels.json"
)


class AccessLevel(BaseModel):
    fields = ["id", "access_level_name"]

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def index(cls, **kwargs):
        return super().index(DATA_FILE, **kwargs)
