import sqlite3
from datetime import datetime
from pprint import pprint
from utils.debug import print_r

class BaseModel:
    # Add your JSON helpers here if needed...

    @classmethod
    def index_sqlite(
        cls,
        db_path,
        table_name,
        fields,
        filters=None,
        search=None,
        pagination=False,
        items_per_page=10,
        page=1,
    ):

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        base_query = f"SELECT {', '.join(fields)} FROM {table_name}"
        where_clauses = []
        params = []

        # -----------------------
        # ADVANCED FILTERS
        # -----------------------
        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue

                # DATE RANGE: field_from, field_to
                if key.endswith("_from"):
                    field = key.replace("_from", "")
                    where_clauses.append(f"{field} >= ?")
                    params.append(value)

                elif key.endswith("_to"):
                    field = key.replace("_to", "")
                    where_clauses.append(f"{field} <= ?")
                    params.append(value)

                else:
                    # Case-insensitive LIKE for normal filters
                    where_clauses.append(f"LOWER({key}) LIKE ?")
                    params.append(f"%{str(value).lower()}%")

        # -----------------------
        # SEARCH (Top-right box)
        # -----------------------
        if search and search.strip() != "":
            search_clauses = [f"LOWER({col}) LIKE ?" for col in fields]
            where_clauses.append("(" + " OR ".join(search_clauses) + ")")
            for _ in fields:
                params.append(f"%{search.lower()}%")

        # Apply WHERE conditions
        final_query = base_query
        if where_clauses:
            final_query += " WHERE " + " AND ".join(where_clauses)

        # -----------------------
        # PAGINATION
        # -----------------------
        total_rows = None
        if pagination:
            total_rows_query = f"SELECT COUNT(*) FROM ({final_query})"
            cursor.execute(total_rows_query, params)
            total_rows = cursor.fetchone()[0]

            offset = (page - 1) * items_per_page
            final_query += f" LIMIT {items_per_page} OFFSET {offset}"

        # Execute main query
        cursor.execute(final_query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert rows → class objects
        data = [cls(**dict(zip(fields, row))) for row in rows]



        # -----------------------
        # DEBUG SQL PRINT
        # -----------------------
        # if table_name == 'users':
            # print("\n====== SQL DEBUG ======")
            # print("SQL:", final_query)
            # print("PARAMS:", params)
            # print("filters:", filters)
            # print("Showing Data count: ", len(data))
            # print_r(data)
            # if pagination:
            #     print("Total Rows:", total_rows)
            # print("=======================\n")



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
    def store_sqlite(cls, db_path, table_name, **kwargs):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["created_at"] = now
        kwargs["updated_at"] = now

        fields = ", ".join(kwargs.keys())
        placeholders = ", ".join("?" for _ in kwargs)
        values = list(kwargs.values())

        cursor.execute(
            f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})", values
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()

        kwargs["id"] = last_id
        return cls(**kwargs)

    @classmethod
    def update_sqlite(cls, db_path, table_name, row_id, **kwargs):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        kwargs["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_clause = ", ".join(f"{key}=?" for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(row_id)

        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return True

    @classmethod
    def destroy_sqlite(cls, db_path, table_name, row_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = f"DELETE FROM {table_name} WHERE id=?"
        cursor.execute(query, (row_id,))
        conn.commit()
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