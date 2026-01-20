import re
import importlib

class RuleValidator:
    @staticmethod
    def validate_field(name, value, rules):
        errors = []

        for rule in rules:
            if rule == 'required':
                if value is None or value == "":
                    errors.append(f"{name} is required.")

            elif rule == 'string':
                if value is not None and not isinstance(value, str):
                    errors.append(f"{name} must be a string.")

            elif rule == 'integer':
                if value is not None:
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"{name} must be an integer.")

            elif rule == 'email':
                if value is not None and not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    errors.append(f"{name} must be a valid email.")

            elif rule.startswith('unique:'):
                try:
                    # Parse "unique:user,username"
                    _, params = rule.split(':')
                    model_parts = params.split(',')
                    model_name = model_parts[0]
                    field = model_parts[1]
                
                    model_module = importlib.import_module(f"models.{model_name}")
                    # PascalCase for class name (e.g. access_level -> AccessLevel)
                    class_name = "".join(part.capitalize() for part in model_name.split("_"))
                    model_class = getattr(model_module, class_name)

                    # Use model's index method with filters
                    existing = model_class.index(filters={field: value})

                    if len(existing) > 0:
                        errors.append(f"{name} must be unique.")
                        
                except Exception as e:
                    errors.append(f"{name} uniqueness check failed: {str(e)}")
                    

        return errors

    @staticmethod
    def validate(data, rules):
        validated_data = {}
        errors = {}

        for field, field_rules in rules.items():
            # Only process if field is in data OR if it's required (to catch missing required fields)
            if field in data or 'required' in field_rules:
                value = data.get(field)
                validated_data[field] = value
                field_errors = RuleValidator.validate_field(field, value, field_rules)

                if field_errors:
                    errors[field] = field_errors

        return validated_data, errors
