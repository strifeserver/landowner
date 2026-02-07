# controllers/MyAccountController.py
from utils.session import Session
from models.user import User
import os
import shutil

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
            if not current_pw or user.password != current_pw:
                return {"success": False, "message": "Incorrect current password"}

        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "email" in data:
            update_data["email"] = data["email"]
        if "new_password" in data and data["new_password"]:
            update_data["password"] = data["new_password"]
        
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
