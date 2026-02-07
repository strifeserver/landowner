from .BaseRequest import BaseRequest
from models.navigation import Navigation

class NavigationsRequest(BaseRequest):
    def common_rules(self):
        return {
            'menu_name': ['required', 'string'],
            'navigation_type': ['required', 'string'],
            'status': ['required', 'string'],
            'navigation_order': ['required', 'integer'],
        }

    def store_rules(self):
        return {}

    def update_rules(self):
        return {}
