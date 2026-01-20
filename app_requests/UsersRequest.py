from .BaseRequest import BaseRequest

class UsersRequest(BaseRequest):
    def common_rules(self):
        """Rules shared by both store and update."""
        return {
            'username': ['string'],
            'email': ['email'],
            'account_status': ['required', 'string'],
            'is_locked': ['required', 'integer'],
            'access_level': ['required', 'integer'],
        }

    def store_rules(self):
        """Rules specific to creating a user."""
        return {
            'customId': ['required', 'string', 'unique:user,customId'],
            'username': ['required', 'string', 'unique:user,username'],
            'password': ['required', 'string'],
        }

    def update_rules(self):
        """Rules specific to updating a user."""
        return {
            'username': ['string'], 
            'password': ['nullable', 'string'],
        }

    def delete_rules(self):
        """Unique rules for deletion (skips common rules)."""
        return {
            # Example: 'confirm': ['required', 'accepted']
        }
