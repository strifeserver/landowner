# controllers/auth_controller.py
from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def login(self, username, password):
        return self.auth_service.authenticate(username, password)
