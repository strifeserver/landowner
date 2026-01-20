class Session:
    _instance = None
    current_user = None
    _listeners = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_user(cls, user):
        cls.current_user = user

    @classmethod
    def get_user(cls):
        return cls.current_user

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
