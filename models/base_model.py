import json
from datetime import datetime

class BaseModel:
    @classmethod
    def index(cls, data_file, filters=None, search=None, pagination=False, items_per_page=10, page=1):
        with open(data_file, 'r') as f:
            data = json.load(f)

        results = []

        for record in data:
            # Global search
            if search:
                if any(search.lower() in str(value).lower() for value in record.values()):
                    results.append(cls(**record))
                continue

            # Advanced filters
            if filters:
                match = True
                for key, value in filters.items():
                    match key:
                        case 'id':
                            try:
                                match = match and int(record.get('id', -1)) == int(value)
                            except ValueError:
                                match = False

                        case 'created_at_from':
                            try:
                                record_date = datetime.strptime(record.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                                from_date = datetime.strptime(value, '%Y-%m-%d')
                                match = match and record_date >= from_date
                            except ValueError:
                                match = False

                        case 'created_at_to':
                            try:
                                record_date = datetime.strptime(record.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                                to_date = datetime.strptime(value, '%Y-%m-%d')
                                match = match and record_date <= to_date
                            except ValueError:
                                match = False

                        case _:
                            match = match and str(record.get(key, '')).lower() == str(value).lower()

                if match:
                    results.append(cls(**record))
                continue

            results.append(cls(**record))

        if pagination:
            start = (page - 1) * items_per_page
            end = start + items_per_page
            return results[start:end]

        return results
        
    @classmethod
    def store(cls, data_file, **kwargs):
        # Load existing data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Determine new ID
        if data:
            max_id = max(record.get('id', 0) for record in data)
            new_id = max_id + 1
        else:
            new_id = 1

        kwargs['id'] = new_id

        # Add timestamps like Laravel format
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kwargs['created_at'] = now
        kwargs['updated_at'] = now

        # Add new record
        data.append(kwargs)

        # Save back to file
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=4)

        return cls(**kwargs)  # return the newly created object
