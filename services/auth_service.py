# services/auth_service.py
import json

class AuthService:
    def __init__(self, user_file="data/users.json"):
        self.user_file = user_file

    def authenticate(self, username, password):
        with open(self.user_file, "r") as f:
            users = json.load(f)
        for user in users:
            if user["username"] == username and user["password"] == password:
                return True
        return False
