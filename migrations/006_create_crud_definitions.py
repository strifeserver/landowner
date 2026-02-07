# migrations/006_create_crud_definitions.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create crud_definitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crud_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            table_name TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            sort_field TEXT,
            sort_direction TEXT DEFAULT 'ASC',
            created_at DATETIMEDEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Link CRUD Builder navigation entry to CrudBuilderController
    cursor.execute("UPDATE navigations SET controller = 'CrudBuilderController' WHERE id = 9")

    conn.commit()
    conn.close()
    print("Migration 006_create_crud_definitions complete.")

if __name__ == "__main__":
    migrate()
