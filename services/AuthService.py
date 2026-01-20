# services/auth_service.py
from models.user import User

class AuthService:
    def __init__(self):
        pass

    def authenticate(self, username, password):
        # Fetch user by username (and simple password check for now)
        # Note: In production use hashed passwords.
        users = User.index(filters={"username": username})
        
        if not users:
            raise ValueError("Invalid credentials")
            
        user = users[0]
        
        # Verify password (plaintext matching seed data)
        if user.password == password:
            if getattr(user, "is_locked", False):
                # Check for SQLite boolean (0/1) or Python boolean
                is_locked = user.is_locked
                if str(is_locked).lower() in ('1', 'true'):
                     raise ValueError("Account is locked")
            
            return user
            
        raise ValueError("Invalid credentials")
