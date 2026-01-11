# services/BaseService.py
from utils.debug import print_r

class BaseService:
    def __init__(self, model):
        self.model = model

    def index(self, filters=None, pagination=False, items_per_page=5, page=1, search=None, debug=False):

        results = self.model.index(
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            debug=debug
        )

        if isinstance(results, dict) and "data" in results:
            data = results["data"]
            total_rows = results["total_rows"]
            total_pages = results["total_pages"]
            last_page = results["last_page"]
        else:
            data = results
            total_rows = len(data)
            total_pages = 1
            last_page = 1

        # Field post-processing (OK to keep)
        if hasattr(self.model, "field_definitions") and self.model.field_definitions:
            for row in data:
                for field_key, field_def in self.model.field_definitions.items():
                    if field_key in row.__dict__:
                        value = row.__dict__[field_key]

                        if field_def.get("capitalize1st") and isinstance(value, str):
                            row.__dict__[field_key] = value[:1].upper() + value[1:]

                        if "subtitute_table_values" in field_def:
                            value_map = {
                                entry["value"]: entry["label"]
                                for entry in field_def["subtitute_table_values"]
                            }
                            row.__dict__[field_key] = value_map.get(value, value)

        return {
            "data": data,              # already paginated
            "total_rows": total_rows,
            "total_pages": total_pages,
            "last_page": last_page,
        }


    def edit(self, id):
        return self.model.edit(id)

    def store(self, data):
        return self.repository.store(data)

    def update(self, id, data):
        # Handle alias fields if model is provided
        # if self.model:
        #     origin_map = {
        #         key: val["origin_field"]
        #         for key, val in self.model.field_definitions.items()
        #         if val.get("origin_field")
        #     }
        #     for alias_field, original_field in origin_map.items():
        #         if alias_field in data:
        #             data[original_field] = data.pop(alias_field)
   
        return self.model.update(id, data)

    def delete(self, id):
        return self.repository.destroy(id)
