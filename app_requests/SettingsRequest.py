from .BaseRequest import BaseRequest

class SettingsRequest(BaseRequest):
    def common_rules(self):
        """Rules shared by both store and update."""
        return {
            'setting_name': ['required', 'string'],
            'setting_value': ['required', 'string'],
        }

    def store_rules(self):
        """Rules specific to creating a setting."""
        return {
            'setting_name': ['unique:Setting,setting_name'],
        }
