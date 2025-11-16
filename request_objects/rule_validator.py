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
                    model_name, field = params.split(',')
                

                    model_module = importlib.import_module(f"models.{model_name}")
                    model_class = getattr(model_module, model_name.capitalize())

                    
                    # Use model's index method with filters
                    existing = model_class.index(filters={field: value})
                    # print('Existing records found for uniqueness check:')
                    # for record in existing:
                    #     print(f"{field} in existing record: {getattr(record, field, None)}")

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
            value = data.get(field)
            validated_data[field] = value
            field_errors = RuleValidator.validate_field(field, value, field_rules)

            if field_errors:
                errors[field] = field_errors

        return validated_data, errors