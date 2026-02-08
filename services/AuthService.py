# services/auth_service.py
from models.user import User
import bcrypt

class AuthService:
    def __init__(self):
        pass

    def authenticate(self, username, password):
        """
        Authenticate user with bcrypt password hashing.
        Supports legacy plaintext passwords and auto-migrates them.
        """
        users = User.index(filters={"username": username})
        
        if not users:
            raise ValueError("Invalid credentials")
            
        user = users[0]
        
        # Check if account is locked
        if getattr(user, "is_locked", False):
            is_locked = user.is_locked
            if str(is_locked).lower() in ('1', 'true'):
                raise ValueError("Account is locked")
        
        # Verify password
        password_valid = False
        needs_rehash = False
        
        stored_password = user.password
        
        # Check if password is bcrypt hash (starts with $2b$ or $2a$)
        if stored_password and (stored_password.startswith('$2b$') or stored_password.startswith('$2a$')):
            # Verify bcrypt hash
            try:
                password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            except Exception:
                password_valid = False
        else:
            # Legacy plaintext password - check and mark for rehashing
            if stored_password == password:
                password_valid = True
                needs_rehash = True
        
        if not password_valid:
            raise ValueError("Invalid credentials")
        
        # Auto-migrate legacy passwords to bcrypt
        if needs_rehash:
            try:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                User.update(user.id, password=hashed.decode('utf-8'))
            except Exception as e:
                # Log but don't fail login if rehashing fails
                print(f"Warning: Failed to rehash password for user {user.id}: {e}")
        
        return user

