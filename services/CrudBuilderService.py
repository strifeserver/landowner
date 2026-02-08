# services/CrudBuilderService.py
import os
import json
import sqlite3
from models.CrudBuilder import CrudBuilder
from models.navigation import Navigation
from services.BaseService import BaseService

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class CrudBuilderService(BaseService):
    def __init__(self):
        super().__init__(CrudBuilder)

    def generate_module(self, data):
        """
        Generates Model, Service, Controller, and Migration for a new module.
        """
        name = data.get("name")
        fields_json = data.get("fields_json") # List of dicts: [ {alias, name, type, visible, editable, options}, ... ]
        sort_field = data.get("sort_field", "id")
        sort_direction = data.get("sort_direction", "ASC")

        if not name:
            return {"success": False, "message": "Name is required"}

        table_name = name.lower().replace(" ", "_")
        
        # 1. Save definition
        builder_record = self.model.store(
            name=name,
            table_name=table_name,
            fields_json=fields_json,
            sort_field=sort_field,
            sort_direction=sort_direction
        )

        # 2. Generate Files
        try:
            # Normalize dropdown values to lowercase
            fields_json = self._normalize_fields(fields_json)

            self._generate_model(name, table_name, fields_json, sort_field, sort_direction)
            self._generate_service(name)
            self._generate_controller(name)
            self._generate_migration(name, table_name, fields_json)
            self._add_navigation(name, table_name)
            self._sync_table_settings(name, table_name, fields_json)
            
            return {"success": True, "builder_id": builder_record.id}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_module(self, id, data):
        """Update definition and regenerate files."""
        name = data.get("name")
        fields_json = data.get("fields_json")
        sort_field = data.get("sort_field", "id")
        sort_direction = data.get("sort_direction", "ASC")

        old_record = self.model.edit(id)
        if not old_record:
            return {"success": False, "message": "Record not found"}

        table_name = old_record.table_name # Assume table name doesn't change for now

        self.model.update(id, name=name, fields_json=fields_json, sort_field=sort_field, sort_direction=sort_direction)

        try:
            # Normalize dropdown values to lowercase
            fields_json = self._normalize_fields(fields_json)

            # Sync database schema first
            self._sync_table_schema(table_name, fields_json)
            
            self._generate_model(name, table_name, fields_json, sort_field, sort_direction)
            self._generate_service(name)
            self._generate_controller(name)
            self._sync_table_settings(name, table_name, fields_json)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_module(self, id):
        record = self.model.edit(id)
        if record:
            name = record.name
            table_name = record.table_name
            class_name = name.replace(" ", "")

            # 1. Delete navigation entry
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM navigations WHERE navigation = ?", (table_name,))
            
            # 2. Delete table settings
            self._delete_table_settings(table_name)
            
            # 3. Drop the table (optional safety: could be skipped, but user requested)
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            except Exception as e:
                pass
            
            conn.commit()
            conn.close()

            # 3. Delete generated files
            files_to_delete = [
                os.path.join("models", f"{class_name}.py"),
                os.path.join("services", f"{class_name}Service.py"),
                os.path.join("controllers", f"{class_name}Controller.py")
            ]
            
            # Find and add migration file
            migration_dir = "migrations"
            if os.path.exists(migration_dir):
                for f in os.listdir(migration_dir):
                    if f.endswith(f"_create_{table_name}_table.py"):
                        files_to_delete.append(os.path.join(migration_dir, f))

            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        pass
            
            # 4. Delete the CRUD definition record
            return self.model.destroy(id)
        return False

    def _generate_model(self, name, table_name, fields_json, sort_field, sort_direction):
        class_name = name.replace(" ", "")
        fields_list = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        
        # Build fields list for the model
        model_fields = ["id"]
        field_defs = {
            "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False}
        }
        
        for i, f in enumerate(fields_list):
            fname = f.get("name")
            model_fields.append(fname)
            field_defs[fname] = {
                "alias": f.get("alias"),
                "order": i + 1,
                "editable": f.get("editable", True),
                "is_hidden": not f.get("visible", True)
            }
            if f.get("type") == "dropdown" and f.get("options"):
                field_defs[fname]["options"] = f.get("options")

        model_fields.extend(["created_at", "updated_at", "created_by", "updated_by"])
        field_defs["created_at"] = {"alias": "Date Created", "order": len(fields_list) + 1, "is_hidden": True}
        field_defs["updated_at"] = {"alias": "Date Updated", "order": len(fields_list) + 2, "is_hidden": True}
        field_defs["created_by_name"] = {"alias": "Created By", "order": len(fields_list) + 3, "editable": False}
        field_defs["updated_by_name"] = {"alias": "Updated By", "order": len(fields_list) + 4, "editable": False}

        import pprint
        formatted_defs = pprint.pformat(field_defs, indent=8)
        content = f"""import os
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class {class_name}(BaseModel):
    table_name = "{table_name}"
    fields = {model_fields}
    field_definitions = {formatted_defs}

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        # Joined fields
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1, **kwargs):
        base_fields = [f"t.{{f}}" for f in cls.fields]
        join_query = f\"\"\"
            SELECT {{', '.join(base_fields)}}, 
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {{cls.table_name}} t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.updated_by = u2.id
        \"\"\"
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]

        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            sort_by=kwargs.get('sort_by', '{sort_field}'),
            sort_order=kwargs.get('sort_order', '{sort_direction}'),
            custom_query=join_query,
            custom_fields=custom_fields,
            table_alias="t"
        )

    @classmethod
    def edit(cls, id):
        base_fields = [f"t.{{f}}" for f in cls.fields]
        join_query = f\"\"\"
            SELECT {{', '.join(base_fields)}}, 
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {{cls.table_name}} t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.updated_by = u2.id
        \"\"\"
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]

        return super().edit_sqlite(
            DB_PATH, 
            cls.table_name, 
            cls.fields, 
            row_id=id,
            custom_query=join_query,
            custom_fields=custom_fields,
            table_alias="t"
        )

    @classmethod
    def store(cls, **kwargs):
        return super().store_sqlite(DB_PATH, cls.table_name, **kwargs)

    @classmethod
    def update(cls, id, **kwargs):
        return super().update_sqlite(DB_PATH, cls.table_name, id, **kwargs)

    @classmethod
    def destroy(cls, id):
        return super().destroy_sqlite(DB_PATH, cls.table_name, id)

    @classmethod
    def get_dynamic_field_definitions(cls):
        return cls.field_definitions
"""
        with open(os.path.join("models", f"{class_name}.py"), "w") as f:
            f.write(content)

    def _generate_service(self, name):
        class_name = name.replace(" ", "")
        content = f"""from models.{class_name} import {class_name}
from services.BaseService import BaseService

class {class_name}Service(BaseService):
    def __init__(self):
        super().__init__({class_name})
"""
        with open(os.path.join("services", f"{class_name}Service.py"), "w") as f:
            f.write(content)

    def _generate_controller(self, name):
        class_name = name.replace(" ", "")
        content = f"""from models.{class_name} import {class_name}
from services.{class_name}Service import {class_name}Service

class {class_name}Controller:
    model = {class_name}
    @staticmethod
    def index(filters=None, pagination=False, items_per_page=10, page=1, searchAll=None):
        service = {class_name}Service()
        return service.index(
            filters=filters or {{}},
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            search=searchAll
        )

    @staticmethod
    def create():
        return {{
            "view_type": "generic",
            "field_definitions": {class_name}.get_dynamic_field_definitions()
        }}

    @staticmethod
    def store(data):
        service = {class_name}Service()        
        result = service.store(data)
        return {{"success": True, "message": "{name} created successfully"}} if result else {{"success": False, "message": "Failed to create {name.lower()}"}}

    @staticmethod
    def edit(data):
        return {{
            "view_type": "generic",
            "field_definitions": {class_name}.get_dynamic_field_definitions(),
            "initial_data": data
        }}

    @staticmethod
    def update(id, data):
        service = {class_name}Service()   
        result = service.update(id, data)
        return {{"success": True, "message": "{name} updated successfully"}} if result else {{"success": False, "message": "Failed to update {name.lower()}"}}

    @staticmethod
    def destroy(id):
        service = {class_name}Service()   
        result = service.delete(id)
        return {{"success": True, "message": "{name} deleted successfully"}} if result else {{"success": False, "message": "Failed to delete {name.lower()}"}}
"""
        with open(os.path.join("controllers", f"{class_name}Controller.py"), "w") as f:
            f.write(content)

    def _generate_migration(self, name, table_name, fields_json):
        fields_list = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for f in fields_list:
            fname = f.get("name")
            ftype = "TEXT"
            if f.get("type") == "number":
                ftype = "REAL"
            cols.append(f"{fname} {ftype}")
        cols.append("created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        cols.append("updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        cols.append("created_by INTEGER")
        cols.append("updated_by INTEGER")
        
        cols_str = ",\n            ".join(cols)
        
        migration_name = f"create_{table_name}_table"
        import time
        ts = int(time.time())
        filename = f"{ts}_{migration_name}.py"
        
        content = f"""import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {cols_str}
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Migration {migration_name} complete.")

if __name__ == "__main__":
    migrate()
"""
        migration_path = os.path.join("migrations", filename)
        with open(migration_path, "w") as f:
            f.write(content)
        
        # Run migration immediately
        import subprocess
        subprocess.run(["python", migration_path])

    def _add_navigation(self, name, table_name):
        class_name = name.replace(" ", "")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get max order
        cursor.execute("SELECT MAX(navigation_order) FROM navigations")
        row = cursor.fetchone()
        max_order = row[0] if row and row[0] is not None else 0
        conn.close()

        # Use Navigation model store() to leverage auto-created_by logic
        try:
            Navigation.store(
                menu_name=name,
                navigation_order=max_order + 1,
                navigation=table_name,
                navigation_type="menu",
                controller=f"{class_name}Controller",
                status="active"
            )
        except Exception as e:
            print(f"Error adding navigation: {e}")
        
        # Notify sidebar to reload
        from utils.session import Session
        Session.notify_observers()

    def _normalize_fields(self, fields_json):
        """Helper to ensure dropdown values are automatically lowercased."""
        if isinstance(fields_json, str):
            try:
                fields_json = json.loads(fields_json)
            except:
                return fields_json
        
        if not isinstance(fields_json, list):
            return fields_json

        for field in fields_json:
            if field.get("type") == "dropdown":
                options = field.get("options")
                if isinstance(options, list):
                    normalized_options = []
                    for opt in options:
                        if isinstance(opt, dict):
                            normalized_options.append(opt)
                        else:
                            normalized_options.append(str(opt).lower())
                    field["options"] = normalized_options
        
        return fields_json

    def _sync_table_schema(self, table_name, fields_json):
        """Adds missing columns to the database table."""
        fields_list = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in cursor.fetchall()]
        
        for f in fields_list:
            fname = f.get("name")
            if fname not in existing_cols:
                ftype = "TEXT"
                if f.get("type") == "number":
                    ftype = "REAL"
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {fname} {ftype}")
        
        # Ensure audit fields exist
        audit_fields = {
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "created_by": "INTEGER",
            "updated_by": "INTEGER"
        }
        for col, col_type in audit_fields.items():
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}")
                
        conn.commit()
        conn.close()

    def _sync_table_settings(self, name, table_name, fields_json):
        """Creates or updates table settings for the module."""
        from models.table_setting import TableSetting
        import json

        fields_list = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        
        # Build initial settings_json
        settings = []
        # Add ID first
        settings.append({
            "name": "id",
            "alias": "ID",
            "visible": True,
            "order": 0,
            "capitalize_first": False
        })
        
        for i, f in enumerate(fields_list):
            settings.append({
                "name": f.get("name"),
                "alias": f.get("alias"),
                "visible": f.get("visible", True),
                "order": i + 1,
                "capitalize_first": False
            })
            
        # Add audit fields
        settings.append({"name": "created_at", "alias": "Date Created", "visible": False, "order": len(fields_list) + 1, "capitalize_first": False})
        settings.append({"name": "updated_at", "alias": "Date Updated", "visible": False, "order": len(fields_list) + 2, "capitalize_first": False})
        settings.append({"name": "created_by_name", "alias": "Created By", "visible": False, "order": len(fields_list) + 3, "capitalize_first": False})
        settings.append({"name": "updated_by_name", "alias": "Updated By", "visible": False, "order": len(fields_list) + 4, "capitalize_first": False})

        existing = TableSetting.fetch_by_table_name(table_name)
        if existing:
            # Update only if settings_json is None or we want to overwrite/sync
            # For now, we sync the structure if it's a CRUD module
            TableSetting.update(existing.id, settings_json=json.dumps(settings), table_description=f"Management for {name}")
        else:
            TableSetting.store(
                table_name=table_name,
                table_description=f"Management for {name}",
                settings_json=json.dumps(settings),
                items_per_page=10,
                table_height=300
            )

    def _delete_table_settings(self, table_name):
        """Removes table settings for the module."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM table_settings WHERE table_name = ?", (table_name,))
        conn.commit()
        conn.close()
