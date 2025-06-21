import sqlite3
from datetime import datetime
class BaseModel:
    # Keep your JSON methods if needed...

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

        query = f"SELECT {','.join(fields)} FROM {table_name}"
        conditions = []
        params = []

        if search:
            like_clause = " OR ".join([f"{field} LIKE ?" for field in fields])
            conditions.append(f"({like_clause})")
            params.extend([f"%{search}%" for _ in fields])

        if filters:
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if pagination:
            offset = (page - 1) * items_per_page
            query += f" LIMIT {items_per_page} OFFSET {offset}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = [cls(**dict(zip(fields, row))) for row in rows]
        return results

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
