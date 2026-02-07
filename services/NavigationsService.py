# services/NavigationsService.py
from services.BaseService import BaseService
from models.navigation import Navigation

class NavigationsService(BaseService):
    def __init__(self):
        super().__init__(Navigation)
