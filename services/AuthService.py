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
        
        # 1. Check spreadsheet validation if enabled
        if getattr(user, 'spreadsheet_validation', 0):
            try:
                from services.GoogleSheetService import GoogleSheetService
                from models.Setting import Setting
                from datetime import datetime, timedelta
                
                # Get validation days setting
                validate_days_setting = Setting.index(filters={"setting_name": "google_sheet_last_login_validate_days"})
                validate_days = 7  # Default
                if validate_days_setting and validate_days_setting[0].setting_value:
                    try:
                        validate_days = int(validate_days_setting[0].setting_value)
                    except ValueError:
                        validate_days = 7
                
                # Check database last_login
                db_last_login = getattr(user, 'last_login', None)
                current_dt = datetime.now()
                should_validate = False
                
                if db_last_login:
                    # Parse database last_login
                    try:
                        db_login_dt = datetime.strptime(db_last_login, "%Y-%m-%d %H:%M:%S")
                        days_since_last_login = (current_dt - db_login_dt).days
                        
                        # Only validate against spreadsheet if it's been >= validate_days since last login
                        if days_since_last_login >= validate_days:
                            should_validate = True
                    except ValueError:
                        # If parsing fails, validate to be safe
                        should_validate = True
                else:
                    # No last login in database - first time login, validate
                    should_validate = True
                
                # Perform spreadsheet validation if needed
                if should_validate:
                    sheet_service = GoogleSheetService()
                    
                    # 1. Update the user's last login date in the sheet
                    # This only succeeds if the user is already in the sheet.
                    success, msg = sheet_service.update_user_login_date(user.id)
                    
                    if not success:
                        # If the user is missing from the sheet, block the login
                        if "not found" in msg.lower():
                            raise ValueError(f"Spreadsheet validation failed: User not found in validation spreadsheet. Please contact administrator.")
                        else:
                            # For other technical errors (connection, API), we log a warning but allow login
                            # to avoid global lockouts due to external service issues.
                            print(f"Warning: Spreadsheet validation error: {msg}")
                    else:
                        print(f"Spreadsheet validation successful: {msg}")
                
            except ValueError as ve:
                # Re-raise validation errors (these should block login)
                raise
            except Exception as e:
                # Log general errors but don't block login unless it's a specific validation failure
                print(f"Warning: Unexpected error during spreadsheet validation: {e}")
        
        # 2. Update last_login timestamp
        try:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            User.update(user.id, last_login=now)
        except Exception as e:
            print(f"Warning: Failed to update last_login for user {user.username}: {e}")
        
        # 2. Auto-migrate legacy passwords to bcrypt
        if needs_rehash:
            try:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                User.update(user.id, password=hashed.decode('utf-8'))
            except Exception as e:
                # Log but don't fail login if rehashing fails
                print(f"Warning: Failed to rehash password for user {user.id}: {e}")
        
        return user

