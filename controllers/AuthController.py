# controllers/auth_controller.py
from services.AuthService import AuthService

class AuthController:
    def __init__(self):
        self.AuthService = AuthService()

    def login(self, username, password):
        return self.AuthService.authenticate(username, password)
