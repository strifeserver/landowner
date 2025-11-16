# services/users_service.py

from repositories.users_repository import UsersRepository
from models.user import User


class UsersService:
    @staticmethod
    def get_users(
        filters=None, pagination=False, items_per_page=5, page=1, search=None
    ):
        results = UsersRepository.find_all(filters, search)
        results = UsersRepository.add_access_level_names(results)

        # Overwrite values in each model instance
        for row in results:
            for field_key, field_def in User.field_definitions.items():
                if field_key in row.__dict__:
                    value = row.__dict__[field_key]

                    # Capitalize first letter
                    if field_def.get("capitalize1st") and isinstance(value, str):
                        row.__dict__[field_key] = value[:1].upper() + value[1:]

                    # Substitute value display
                    if "subtitute_table_values" in field_def:
                        value_map = {
                            entry["value"]: entry["label"]
                            for entry in field_def["subtitute_table_values"]
                        }
                        row.__dict__[field_key] = value_map.get(value, value)

        if pagination:
            start = (page - 1) * items_per_page
            end = start + items_per_page
            return results[start:end]

        return results

    @staticmethod
    def get_user(id):
        return UsersRepository.find_by_id(id)

    @staticmethod
    def store_user(data):
        return UsersRepository.store(data)

    @staticmethod
    def update_user(id, data):
        # Map alias fields like 'access_level_name' back to their original fields
        origin_map = {
            key: val["origin_field"]
            for key, val in User.field_definitions.items()
            if val.get("origin_field")
        }

        for alias_field, original_field in origin_map.items():
            if alias_field in data:
                data[original_field] = data.pop(alias_field)

        return UsersRepository.update(id, data)

    @staticmethod
    def delete_user(id):
        return UsersRepository.destroy(id)
