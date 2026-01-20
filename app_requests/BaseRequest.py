from .RuleValidator import RuleValidator

class BaseRequest:
    def __init__(self, data, action='store'):
        self.original_data = data
        self.action = action
        self.validated_data = {}
        self.errors = {}

    def common_rules(self):
        """Rules shared between store and update."""
        return {}

    def store_rules(self):
        """Rules specific to storing."""
        return {}

    def update_rules(self):
        """Rules specific to updating."""
        return {}

    def delete_rules(self):
        """Rules specific to deleting (unique)."""
        return {}

    def get_rules(self):
        """Merge rules based on action."""
        if self.action == 'delete':
            # Delete rules are unique and do not merge with common
            return self.delete_rules()
            
        rules = self.common_rules().copy()
        
        if self.action == 'store':
            rules.update(self.store_rules())
        elif self.action == 'update':
            rules.update(self.update_rules())
            
        return rules

    def validate(self):
        rules = self.get_rules()
        self.validated_data, self.errors = RuleValidator.validate(self.original_data, rules)
        return True if not self.errors else self.errors

    def get_validated_data(self):
        return self.validated_data

    def get_errors(self):
        return self.errors
