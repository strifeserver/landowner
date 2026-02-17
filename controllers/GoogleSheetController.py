from services.GoogleSheetService import GoogleSheetService
from views.google_sheets.google_sheets_view import GoogleSheetsView

class GoogleSheetController:
    @staticmethod
    def index_view(parent):
        """Returns the custom view for Google Sheets integration."""
        return GoogleSheetsView(parent, controller=GoogleSheetController)

    @staticmethod
    def index(**kwargs):
        """Fallback for generic table rendering if called."""
        return []

    @staticmethod
    def validate_connection_logic():
        """Invoke the service to validate Google Sheets connection."""
        service = GoogleSheetService()
        return service.validate_connection()
