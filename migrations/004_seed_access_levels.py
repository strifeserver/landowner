# migrations/004_seed_access_levels.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    access_levels = [
        {
            "id": 1,
            "access_level_name": "Administrator",
            "access_level_code": "admin",
            "view": "1,2,3,4",
            "add": "1,2,3,4",
            "edit": "1,2,3,4",
            "delete": "1,2,3,4",
            "export": "1,2,3,4",
            "import": "1,2,3,4",
        },
        {
            "id": 2,
            "access_level_name": "Staff",
            "access_level_code": "staff",
            "view": "1,2,3,4",
            "add": "1,2,3,4",
            "edit": "1,2,3,4",
            "delete": "",
            "export": "1,2,3,4",
            "import": "",
        },
        {
            "id": 3,
            "access_level_name": "Tenant",
            "access_level_code": "tenant",
            "view": "",
            "add": "",
            "edit": "",
            "delete": "",
            "export": "",
            "import": "",
        },
    ]

    for level in access_levels:
        cursor.execute("""
            INSERT INTO access_levels (
                id, access_level_name, access_level_code,
                view, "add", "edit", "delete", "export", "import",
                created_at, updated_at
            ) VALUES (
                :id, :access_level_name, :access_level_code,
                :view, :add, :edit, :delete, :export, :import,
                DATETIME('now'), DATETIME('now')
            )
        """, level)

    conn.commit()
    conn.close()
    print("Migration 004_seed_access_levels complete.")

if __name__ == "__main__":
    migrate()
