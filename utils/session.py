import os
import json
from datetime import datetime, timedelta

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "session.json")

class Session:
    _instance = None
    current_user = None
    _listeners = []
    _expires_at = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_user(cls, user):
        cls.current_user = user
        cls._expires_at = datetime.now() + timedelta(hours=3)
        cls.save_session()

    @classmethod
    def get_user(cls):
        if cls.current_user is None:
            cls.load_session()
        
        if cls._expires_at and datetime.now() > cls._expires_at:
            cls.clear_session()
            return None
            
        return cls.current_user

    @classmethod
    def save_session(cls):
        if cls.current_user:
            data = {
                "user_id": cls.current_user.id,
                "expires_at": cls._expires_at.isoformat()
            }
            with open(SESSION_FILE, "w") as f:
                json.dump(data, f)

    @classmethod
    def load_session(cls):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                
                expires_at = datetime.fromisoformat(data["expires_at"])
                if datetime.now() < expires_at:
                    from models.user import User
                    user = User.edit(data["user_id"])
                    if user:
                        cls.current_user = user
                        cls._expires_at = expires_at
                        return True
                else:
                    cls.clear_session()
            except Exception as e:
                print(f"Error loading session: {e}")
                cls.clear_session()
        return False

    @classmethod
    def clear_session(cls):
        cls.current_user = None
        cls._expires_at = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    @classmethod
    def subscribe(cls, callback):
        """Register a callback function to be called on permission updates."""
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def notify_permission_change(cls):
        """Invoke all registered callbacks to refresh UI."""
        for callback in cls._listeners:
            try:
                callback()
            except Exception as e:
                print(f"Error in session callback: {e}")

    @classmethod
    def notify_observers(cls):
        """Alias for notify_permission_change to maintain compatibility."""
        cls.notify_permission_change()
