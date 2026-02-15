import sqlite3
from datetime import datetime
from pprint import pprint
from utils.debug import print_r

class BaseModel:
    # Add your JSON helpers here if needed...

    @classmethod
    def get_ambiguous_fields(cls):
        """
        Returns a list of fields that need table alias prefix to avoid ambiguity
        """
        # Common fields across tables that might collide in joins
        return ["id", "created_at", "updated_at"]




    @classmethod
    def index_sqlite(
        cls,
        db_path,
        target_table,
        fields,
        custom_fields=None,
        filters=None,
        search=None,
        pagination=False,
        items_per_page=10,
        page=1,
        sort_by="id",
        sort_order="DESC",
        custom_query=None,
        table_alias=None,
        debug=False,
        conn=None,
        **kwargs,
    ):
        """
        Generic SQLite SELECT handler with optional LEFT JOINs, filters, search, sorting, and pagination.

        Args:
            db_path (str): Path to SQLite database
            target_table (str): Main table name
            fields (list): List of main table fields
            filters (dict): Filters in key=value form
            search (str): Search term applied across all selected fields
            pagination (bool): Whether to paginate
            items_per_page (int): Number of items per page
            page (int): Page number (1-based)
            custom_query (str): Custom SELECT query (overrides default SELECT)
            custom_fields (list): Fields corresponding to custom_query for mapping
            debug (bool): Print SQL debug info
            table_alias (str): Alias for main table (used in joins and ambiguous fields)
            sort_by (str): Field name to sort by
            sort_order (str): Sort direction ('ASC' or 'DESC')
        """
        import sqlite3

        if conn:
            should_close = False
        else:
            conn = sqlite3.connect(db_path)
            should_close = True
            
        cursor = conn.cursor()

        final_fields = custom_fields or fields
        
        if custom_query:
            base_query = custom_query
        else:
            quoted_fields = [f'"{f}"' for f in fields]
            base_query = f"SELECT {', '.join(quoted_fields)} FROM {target_table}"

        # Use alias if provided, else default to target_table
        alias = table_alias or target_table

        # Get ambiguous fields from the model
        ambiguous_fields = getattr(cls, "get_ambiguous_fields", lambda: [])()

        where_clauses = []
        params = []

        # -----------------------
        # Filters
        # -----------------------
        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue

                # Automatically prefix fields to avoid ambiguity if table_alias/alias is provided
                # We prefix if the key is explicitly ambiguous OR if it exists in our main table fields
                is_ambiguous = key in ambiguous_fields or (fields and key in fields)
                field_name = f"{alias}.{key}" if is_ambiguous else key

                if key.endswith("_from"):
                    field_name = field_name.replace("_from", "")
                    where_clauses.append(f"{field_name} >= ?")
                    params.append(value)
                elif key.endswith("_to"):
                    field_name = field_name.replace("_to", "")
                    where_clauses.append(f"{field_name} <= ?")
                    params.append(value)
                else:
                    where_clauses.append(f"LOWER({field_name}) LIKE ?")
                    params.append(f"%{str(value).lower()}%")

        # -----------------------
        # Search
        # -----------------------
        if search and search.strip() != "":
            search_clauses = [
                f"LOWER({alias}.{col}) LIKE ?" if col in ambiguous_fields else f"LOWER({col}) LIKE ?"
                for col in final_fields
            ]
            where_clauses.append("(" + " OR ".join(search_clauses) + ")")
            for _ in final_fields:
                params.append(f"%{search.lower()}%")

        # -----------------------
        # Apply WHERE
        # -----------------------
        # -----------------------
        # Apply WHERE
        # -----------------------
        final_query = base_query
        
        if where_clauses:
            # Check if WHERE already exists (case-insensitive)
            if " WHERE " in final_query.upper():
                connector = " AND "
            else:
                connector = " WHERE "
            
            final_query += connector + " AND ".join(where_clauses)

        # -----------------------
        # Apply ORDER BY
        # -----------------------
        if sort_by:
            # Check if ORDER BY already exists (case-insensitive)
            # If custom_query has ORDER BY, we need to handle it or append?
            # Usually custom_query is just SELECT ... FROM ... JOIN ...
            # But just in case:
            if " ORDER BY " in final_query.upper():
                 # Complex to merge orders. Assume custom_query doesn't sort, or we append secondary sort
                 final_query += f", {sort_field} {sort_order}"
            else:
                 # Automatically prefix ambiguous fields with main table alias
                 sort_field = f"{alias}.{sort_by}" if sort_by in ambiguous_fields else sort_by
                 # Validate sort_order
                 sort_order = sort_order.upper() if sort_order.upper() in ['ASC', 'DESC'] else 'ASC'
                 final_query += f" ORDER BY {sort_field} {sort_order}"

        # -----------------------
        # Pagination
        # -----------------------
        total_rows = None
        if pagination:
            # Use subquery to count correctly even with complex joins/group by
            total_rows_query = f"SELECT COUNT(*) FROM ({final_query})"
            cursor.execute(total_rows_query, params)
            total_rows = cursor.fetchone()[0]

            offset = (page - 1) * items_per_page
            final_query += f" LIMIT {items_per_page} OFFSET {offset}"

        # -----------------------
        # Execute query
        # -----------------------

        cursor.execute(final_query, params)
        rows = cursor.fetchall()
        
        if should_close:
            conn.close()

        # Map rows → class objects
        data = [cls(**dict(zip(final_fields, row))) for row in rows]

        # -----------------------
        # Debug
        # -----------------------

        # -----------------------
        # Conditional return
        # -----------------------
        if pagination:
            return {
                "data": data,
                "total_rows": total_rows,
                "total_pages": (total_rows + items_per_page - 1) // items_per_page,
                "last_page": page,
            }

        return data



    @classmethod
    def edit_sqlite(
        cls,
        db_path,
        target_table,
        fields,
        row_id=None,
        filters=None,
        custom_query=None,
        custom_fields=None,
        table_alias=None,
        debug=False,
        conn=None,
    ):
        """
        Fetch a single row from SQLite, either by ID or custom filters.

        Args:
            db_path (str): Path to SQLite database
            target_table (str): Table name
            fields (list): List of fields to select
            row_id (int, optional): ID of row to fetch
            filters (dict, optional): Other key=value filters
            custom_query (str, optional): Custom SELECT query
            custom_fields (list, optional): Map SELECT columns → object attributes
            table_alias (str, optional): Alias for main table
            debug (bool, optional): Print debug info

        Returns:
            Single object of cls or None
        """
        if conn:
            should_close = False
        else:
            conn = sqlite3.connect(db_path)
            should_close = True
            
        cursor = conn.cursor()

        if custom_fields:
            final_fields = custom_fields 
        else:
             final_fields = fields

        if custom_query:
            base_query = custom_query
        else:
            # Quote fields to avoid reserved keyword issues (e.g. "add")
            quoted_fields = [f'"{f}"' for f in fields]
            base_query = f"SELECT {', '.join(quoted_fields)} FROM {target_table}"
        alias = table_alias or target_table

        where_clauses = []
        params = []

        # ID filter
        if row_id is not None:
            if "id" in getattr(cls, "get_ambiguous_fields", lambda: [])():
                where_clauses.append(f"{alias}.id = ?")
            else:
                where_clauses.append("id = ?")
            params.append(row_id)

        # Other filters
        if filters:
            ambiguous_fields = getattr(cls, "get_ambiguous_fields", lambda: [])()
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                # Automatically prefix fields to avoid ambiguity
                is_ambiguous = key in ambiguous_fields or (fields and key in fields)
                field_name = f"{alias}.{key}" if is_ambiguous else key
                where_clauses.append(f"{field_name} = ?")
                params.append(value)

        # Build final query
        final_query = base_query
        
        if where_clauses:
            # Check if WHERE already exists (case-insensitive)
            if " WHERE " in final_query.upper():
                connector = " AND "
            else:
                connector = " WHERE "
                
            final_query += connector + " AND ".join(where_clauses)
            
        final_query += " LIMIT 1"  # always fetch only one


        cursor.execute(final_query, params)
        row = cursor.fetchone()
        
        if should_close:
            conn.close()

        if row:
            return cls(**dict(zip(final_fields, row)))
        return None




    @classmethod
    def store_sqlite(cls, db_path, target_table, conn=None, **kwargs):
        if conn:
            should_close = False
        else:
            conn = sqlite3.connect(db_path)
            should_close = True
            
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["created_at"] = now
        kwargs["updated_at"] = now

        # Tracking created_by and updated_by
        try:
            from utils.session import Session
            user = Session.get_user()
            if user:
                model_fields = getattr(cls, "fields", [])
                if "created_by" in model_fields:
                    kwargs["created_by"] = user.id
                if "updated_by" in model_fields:
                    kwargs["updated_by"] = user.id
        except Exception:
            pass

        # Filter kwargs to only include valid database fields
        model_fields = getattr(cls, "fields", [])
        if model_fields:
            kwargs = {k: v for k, v in kwargs.items() if k in model_fields}

        fields = ", ".join(f'"{key}"' for key in kwargs.keys())
        placeholders = ", ".join("?" for _ in kwargs)
        values = list(kwargs.values())

        cursor.execute(
            f"INSERT INTO {target_table} ({fields}) VALUES ({placeholders})", values
        )
        
        if should_close or not conn.in_transaction:
            conn.commit()
            
        last_id = cursor.lastrowid
        
        if should_close:
            conn.close()

        kwargs["id"] = last_id
        return cls(**kwargs)

    @classmethod
    def update_sqlite(cls, db_path, target_table, row_id, conn=None, **kwargs):
        if conn:
            should_close = False
        else:
            conn = sqlite3.connect(db_path)
            should_close = True
            
        cursor = conn.cursor()

        kwargs["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Tracking updated_by
        try:
            from utils.session import Session
            user = Session.get_user()
            if user:
                model_fields = getattr(cls, "fields", [])
                if "updated_by" in model_fields:
                    kwargs["updated_by"] = user.id
        except Exception:
            pass

        # Filter kwargs to only include valid database fields
        model_fields = getattr(cls, "fields", [])
        if model_fields:
            kwargs = {k: v for k, v in kwargs.items() if k in model_fields}

        set_clause = ", ".join(f'"{key}"=?' for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(row_id)

        query = f"UPDATE {target_table} SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        
        if should_close or not conn.in_transaction:
            conn.commit()
            
        if should_close:
            conn.close()

        return True

    @classmethod
    def destroy_sqlite(cls, db_path, target_table, row_id, conn=None):
        if conn:
            should_close = False
        else:
            conn = sqlite3.connect(db_path)
            should_close = True
            
        cursor = conn.cursor()

        query = f"DELETE FROM {target_table} WHERE id=?"
        cursor.execute(query, (row_id,))
        
        if should_close or not conn.in_transaction:
            conn.commit()
            
        if should_close:
            conn.close()

        return True



    @classmethod
    def get_visible_fields(cls):
        """
        Returns:
            A sorted list of tuples: (field_name, alias)
        - alias optional → defaults to Title Case of field name
        - is_hidden optional → defaults to False
        - order optional → defaults to 999
        - field_definitions optional → returns empty list
        """
        # If model has NO field definitions → avoid crash
        field_defs = getattr(cls, "field_definitions", {})
        if not isinstance(field_defs, dict):
            return []

        visible_fields = []

        for key, val in field_defs.items():
            # val might not be a dict (bad input)
            if not isinstance(val, dict):
                val = {}

            is_hidden = val.get("is_hidden", False)
            if is_hidden:
                continue

            alias = val.get("alias") or key.replace("_", " ").title()
            order = val.get("order", 999)

            visible_fields.append((key, alias, order))

        # Sort using order
        visible_fields.sort(key=lambda x: x[2])

        # Remove order before returning
        return [(key, alias) for key, alias, _ in visible_fields]


    @classmethod
    def get_ordered_field_keys(cls):
        """Returns only ordered field names."""
        return [key for key, _ in cls.get_visible_fields()]