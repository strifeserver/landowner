# controllers/MyAccountController.py
from utils.session import Session
from models.user import User
import os
import shutil
import bcrypt

class MyAccountController:
    @staticmethod
    def index_view(parent):
        from views.my_account.my_account_view import MyAccountView
        return MyAccountView(parent)

    @staticmethod
    def get_current_user():
        return Session.get_user()

    @staticmethod
    def update_profile(data):
        user = Session.get_user()
        if not user:
            return {"success": False, "message": "No active session"}

        # Validate current password strictly for password changes ONLY
        if "new_password" in data:
            current_pw = data.get("current_password")
            stored_pw = user.password
            
            # Verify current password (support both bcrypt and legacy plaintext)
            password_valid = False
            if stored_pw and (stored_pw.startswith('$2b$') or stored_pw.startswith('$2a$')):
                try:
                    password_valid = bcrypt.checkpw(current_pw.encode('utf-8'), stored_pw.encode('utf-8'))
                except Exception:
                    password_valid = False
            else:
                password_valid = (stored_pw == current_pw)
            
            if not password_valid:
                return {"success": False, "message": "Incorrect current password"}

        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "email" in data:
            update_data["email"] = data["email"]
        if "new_password" in data and data["new_password"]:
            # Hash the new password
            hashed = bcrypt.hashpw(data["new_password"].encode('utf-8'), bcrypt.gensalt())
            update_data["password"] = hashed.decode('utf-8')
        
        # Handle Photo Upload
        if "display_photo_path" in data and data["display_photo_path"]:
            try:
                photo_path = data["display_photo_path"]
                ext = os.path.splitext(photo_path)[1]
                filename = f"user_{user.id}{ext}"
                dest_dir = os.path.join("assets", "images", "profiles")
                dest_path = os.path.join(dest_dir, filename)
                
                # Copy file to project assets
                shutil.copy2(photo_path, dest_path)
                update_data["display_photo"] = os.path.join("profiles", filename)
            except Exception as e:
                return {"success": False, "message": f"Photo upload failed: {e}"}

        if update_data:
            User.update(user.id, **update_data)
            # Refresh session user
            updated_user = User.edit(user.id)
            Session.set_user(updated_user)
            Session.notify_observers()
            return {"success": True, "message": "Profile updated successfully"}
        
        return {"success": False, "message": "No changes provided"}
