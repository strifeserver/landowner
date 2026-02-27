# services/UsersService.py

from models.user import User
from services.BaseService import BaseService

class UsersService(BaseService):
    def __init__(self):
        super().__init__(User)

    def store(self, data):
        """Create a new user and sync to Google Sheets if spreadsheet_validation is enabled."""
        # Call parent store method
        result = super().store(data)
        
        if result:
            # Check if spreadsheet_validation is enabled
            if data.get('spreadsheet_validation'):
                try:
                    from services.GoogleSheetService import GoogleSheetService
                    # Fetch the newly created user
                    user = User.edit(result)
                    if user:
                        sheet_service = GoogleSheetService()
                        success, msg = sheet_service.sync_user_to_sheet(user)
                        if not success:
                            # TODO: Log this warning
                            pass
                except Exception as e:
                    # TODO: Log error
                    pass
        
        return result

    def update(self, id, data):
        """Update a user and sync to Google Sheets if spreadsheet_validation is enabled."""
        # Call parent update method
        result = super().update(id, data)
        
        if result:
            # Fetch the updated user
            user = User.edit(id)
            if user and getattr(user, 'spreadsheet_validation', 0):
                try:
                    from services.GoogleSheetService import GoogleSheetService
                    sheet_service = GoogleSheetService()
                    success, msg = sheet_service.sync_user_to_sheet(user)
                    if not success:
                        # TODO: Log this warning
                        pass
                except Exception as e:
                    # TODO: Log error
                    pass
        
        return result
