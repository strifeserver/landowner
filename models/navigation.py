import os
from models.base_model import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.db')

class Navigation(BaseModel):
    table_name = "navigations"
    fields = ['id', 'menu_name', 'navigation', 'controller', 'navigation_type', 'navigation_order', 'parent_id', 'icon', 'tooltip', 'is_hidden', 'status', 'created_at', 'updated_at', 'created_by', 'updated_by']

    field_definitions = {
        "id": {"alias": "ID", "is_hidden": False, "order": 0, "editable": False},
        "menu_name": {"alias": "Menu Name", "order": 1, "editable": True},
        "navigation": {"alias": "Navigation Slug", "order": 2, "editable": True},
        "controller": {"alias": "Controller", "order": 3, "editable": True},
        "navigation_type": {
            "alias": "Type",
            "order": 4, 
            "editable": True,
            "is_hidden": False,
            "options": ["menu", "parent_menu", "child_menu", "menu_header"]
        },
        "navigation_order": {"alias": "Order", "order": 5, "editable": True},
        "parent_id": {
            "alias": "Parent Menu", 
            "order": 6, 
            "editable": True,
            "options": [] # Populated dynamically
        },
        "icon": {"alias": "Icon", "is_hidden": True, "editable": True},
        "tooltip": {"alias": "Tooltip", "is_hidden": True, "editable": True},
        "is_hidden": {
            "alias": "Hidden", 
            "order": 7, 
            "editable": True,
            "options": [
                {"label": "True", "value": 1},
                {"label": "False", "value": 0}
            ],
            "subtitute_table_values": [
                {"label": "Yes", "value": 1},
                {"label": "No", "value": 0},
            ]
        },
        "status": {
            "alias": "Status", 
            "order": 8, 
            "editable": True,
            "is_hidden": False,
            "options": ["active", "inactive"]
        },
        "created_at": {"alias": "Created", "order": 9, "is_hidden": True},
        "updated_at": {"alias": "Updated", "order": 10, "is_hidden": True},
        "created_by_name": {"alias": "Created By", "order": 11, "editable": False},
        "updated_by_name": {"alias": "Updated By", "order": 12, "editable": False},
    }

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        self.created_by_name = kwargs.get("created_by_name")
        self.updated_by_name = kwargs.get("updated_by_name")

    @classmethod
    def index(cls, filters=None, search=None, pagination=False, items_per_page=10, page=1, **kwargs):
        debug = kwargs.get('debug', False)
        sort_by = kwargs.get('sort_by', 'navigation_order')
        sort_order = kwargs.get('sort_order', 'ASC')
        
        # Default SELECT query if no custom_query
        if not kwargs.get('custom_query'):
            table_alias = kwargs.get('table_alias', 't')
            prefix = f"{table_alias}."
            fields_to_select = [f'{prefix}"{f}"' for f in cls.fields]
            select_clause = ", ".join(fields_to_select)
            
            kwargs['custom_query'] = f"""
                SELECT {select_clause},
                       COALESCE(u1.name, u1.username) as created_by_name,
                       COALESCE(u2.name, u2.username) as updated_by_name
                FROM {cls.table_name} {table_alias}
                LEFT JOIN users u1 ON {table_alias}.created_by = u1.id
                LEFT JOIN users u2 ON {table_alias}.updated_by = u2.id
            """
            kwargs['custom_fields'] = cls.fields + ["created_by_name", "updated_by_name"]
            kwargs['table_alias'] = table_alias

        return super().index_sqlite(
            DB_PATH,
            cls.table_name,
            cls.fields,
            filters=filters,
            search=search,
            pagination=pagination,
            items_per_page=items_per_page,
            page=page,
            debug=debug,
            sort_by=sort_by,
            sort_order=sort_order,
            custom_query=kwargs.get('custom_query'),
            custom_fields=kwargs.get('custom_fields'),
            table_alias=kwargs.get('table_alias')
        )

    @classmethod
    def edit(cls, id, **kwargs):
        table_alias = "t"
        prefix = f"{table_alias}."
        fields_to_select = [f'{prefix}"{f}"' for f in cls.fields]
        select_clause = ", ".join(fields_to_select)
        
        custom_query = f"""
            SELECT {select_clause},
                   COALESCE(u1.name, u1.username) as created_by_name,
                   COALESCE(u2.name, u2.username) as updated_by_name
            FROM {cls.table_name} {table_alias}
            LEFT JOIN users u1 ON {table_alias}.created_by = u1.id
            LEFT JOIN users u2 ON {table_alias}.updated_by = u2.id
        """
        custom_fields = cls.fields + ["created_by_name", "updated_by_name"]
        
        return super().edit_sqlite(
            DB_PATH, 
            cls.table_name, 
            cls.fields, 
            row_id=id, 
            custom_query=custom_query, 
            custom_fields=custom_fields,
            table_alias=table_alias
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
        """Injects parent_id options dynamically."""
        field_defs = dict(cls.field_definitions)
        
        try:
            # Get all parent menus
            parents = cls.index(filters={"navigation_type": "parent_menu"})
            options = [{"label": "None", "value": None}]
            if parents:
                options.extend([{"label": p.menu_name, "value": p.id} for p in parents])
            
            field_defs["parent_id"]["options"] = options
        except Exception:
            field_defs["parent_id"]["options"] = []
            
        return field_defs

    @classmethod
    def move_up(cls, id):
        """
        Move a navigation item 'Up' the list (visually) by swapping with the previous item (smaller order).
        Returns True if successful, False otherwise.
        """
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current item
            current_item = cls.edit(id)
            if not current_item or current_item.navigation_order is None:
                conn.close()
                return False
            
            current_order = int(current_item.navigation_order)
            
            # Find the item with the next lower order (to swap with - move up)
            cursor.execute(
                f"SELECT id, navigation_order FROM {cls.table_name} WHERE navigation_order < ? ORDER BY navigation_order DESC LIMIT 1",
                (current_order,)
            )
            prev_item = cursor.fetchone()
            
            if prev_item:
                prev_id, prev_order = prev_item
                
                # Swap the orders
                cursor.execute(f"UPDATE {cls.table_name} SET navigation_order = ? WHERE id = ?", (prev_order, id))
                cursor.execute(f"UPDATE {cls.table_name} SET navigation_order = ? WHERE id = ?", (current_order, prev_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            print(f"Error moving navigation up: {e}")
            return False

    @classmethod
    def move_down(cls, id):
        """
        Move a navigation item 'Down' the list (visually) by swapping with the next item (larger order).
        Returns True if successful, False otherwise.
        """
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get current item
            current_item = cls.edit(id)
            if not current_item or current_item.navigation_order is None:
                conn.close()
                return False
            
            current_order = int(current_item.navigation_order)
            
            # Find the item with the next higher order (to swap with - move down)
            cursor.execute(
                f"SELECT id, navigation_order FROM {cls.table_name} WHERE navigation_order > ? ORDER BY navigation_order ASC LIMIT 1",
                (current_order,)
            )
            next_item = cursor.fetchone()
            
            if next_item:
                next_id, next_order = next_item
                
                # Swap the orders
                cursor.execute(f"UPDATE {cls.table_name} SET navigation_order = ? WHERE id = ?", (next_order, id))
                cursor.execute(f"UPDATE {cls.table_name} SET navigation_order = ? WHERE id = ?", (current_order, next_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            print(f"Error moving navigation down: {e}")
            return False
