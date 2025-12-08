# from repositories.settings_repository import SettingsRepository
from repositories.users_repository import UsersRepository
from models.user import User
from services.BaseService import BaseService

class SettingsService(BaseService):
    def __init__(self):
        super().__init__(UsersRepository, User)

    # Override fetch_data for SettingsService
    def index(self, filters=None, pagination=False, items_per_page=5, page=1, search=None):
        # You can modify filters, transform results, or add extra behavior
        # if filters is None:
        #     filters = {}

        # # Example: automatically only return active settings
        # filters["status"] = filters.get("status", "active")

        # Call the BaseService fetch_data to do the main work
        result = super().index(
            filters=filters,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=search
        )

        # Example: add extra info to the result
        result["note"] = "This is SettingsService customized index"

        return result
