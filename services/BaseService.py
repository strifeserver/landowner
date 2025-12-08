# services/BaseService.py

class BaseService:
    
    
    def __init__(self, repository, model=None):

        self.repository = repository
        self.model = model

 
    def index(self, filters=None, pagination=False, items_per_page=5, page=1, search=None):
        results = self.repository.find_all(filters, search)
        
        # Optional: add access level names or any other repo-specific processing
        if hasattr(self.repository, "add_access_level_names"):
            results = self.repository.add_access_level_names(results)
        
        # Process fields if model is provided
        if self.model:
            for row in results:
                for field_key, field_def in self.model.field_definitions.items():
                    if field_key in row.__dict__:
                        value = row.__dict__[field_key]

                        if field_def.get("capitalize1st") and isinstance(value, str):
                            row.__dict__[field_key] = value[:1].upper() + value[1:]

                        if "subtitute_table_values" in field_def:
                            value_map = {entry["value"]: entry["label"] for entry in field_def["subtitute_table_values"]}
                            row.__dict__[field_key] = value_map.get(value, value)

        total_rows = len(results)
        total_pages = (total_rows + items_per_page - 1) // items_per_page
        last_page = total_pages

        if pagination:
            start = (page - 1) * items_per_page
            end = start + items_per_page
            page_data = results[start:end]
        else:
            page_data = results

        return {
            "data": page_data,
            "total_rows": total_rows,
            "total_pages": total_pages,
            "last_page": last_page,
        }

    def fetch_one(self, id):
        return self.repository.find_by_id(id)

    def store(self, data):
        return self.repository.store(data)

    def update(self, id, data):
        # Handle alias fields if model is provided
        if self.model:
            origin_map = {
                key: val["origin_field"]
                for key, val in self.model.field_definitions.items()
                if val.get("origin_field")
            }
            for alias_field, original_field in origin_map.items():
                if alias_field in data:
                    data[original_field] = data.pop(alias_field)

        return self.repository.update(id, data)

    def delete(self, id):
        return self.repository.destroy(id)
