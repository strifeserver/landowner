# services/users_service.py

from repositories.users_repository import UsersRepository


class UsersService:
    @staticmethod
    def get_users(
        filters=None, pagination=False, items_per_page=5, page=1, search=None
    ):
        results = UsersRepository.find_all(filters, search)
        results = UsersRepository.add_access_level_names(results)

        if pagination:
            start = (page - 1) * items_per_page
            end = start + items_per_page
            return results[start:end]

        return results

    @staticmethod
    def get_user(id):
        results = UsersRepository.find_by_id(id)
        return results
