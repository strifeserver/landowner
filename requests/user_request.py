# user_request.py
from models.user import User
from .rule_validator import RuleValidator

class UserRequest:
    def __init__(self, data, action='store'):
        self.original_data = data
        self.validated_data = {}
        self.errors = {}
        self.action = action

    def rules(self):
        if self.action == 'store':
            return {
                'username': ['required', 'string', 'unique:user,username'],
                'password': ['nullable', 'string'],
                'last_name': ['required', 'string'],
            }
        elif self.action == 'update':
            return {
                'username': ['string'],
                'email': ['email'],
            }
        return {}

    def validate(self):
        self.validated_data, self.errors = RuleValidator.validate(self.original_data, self.rules())
        return True if not self.errors else self.errors

    def get_validated_data(self):
        return self.validated_data

    def get_errors(self):
        return self.errors
