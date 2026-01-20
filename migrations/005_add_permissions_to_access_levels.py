# migrations/005_add_permissions_to_access_levels.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List of new columns to check/add
    new_columns = ["view", "add", "edit", "delete", "export", "import"]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(access_levels)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    for col in new_columns:
        if col not in existing_columns:
            print(f"Adding column '{col}' to access_levels table...")
            # SQLite supports ADD COLUMN but requires double quotes for reserved keywords like "add" or "view"
            cursor.execute(f'ALTER TABLE access_levels ADD COLUMN "{col}" TEXT DEFAULT ""')

    conn.commit()
    conn.close()
    print("Migration 005_add_permissions_to_access_levels complete.")

if __name__ == "__main__":
    migrate()
