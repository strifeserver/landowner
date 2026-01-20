# controllers/auth_controller.py
from services.AuthService import AuthService

class AuthController:
    @staticmethod
    def login(username, password):
        service = AuthService()
        return service.authenticate(username, password)
