import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create table_settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT UNIQUE NOT NULL,
            table_description TEXT,
            settings_json TEXT, -- JSON array of column configs
            items_per_page INTEGER DEFAULT 10,
            table_height INTEGER DEFAULT 300,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER
        )
    """)

    # 2. Seed default settings for core tables
    # For each core table, we'll initialize it with default settings if not exists
    core_tables = [
        ("users", "User accounts management"),
        ("navigations", "System navigation and menu structure"),
        ("settings", "Global application settings"),
        ("access_levels", "Role-based permissions management"),
        ("crud_definitions", "Metadata for dynamically generated modules"),
        ("table_settings", "Configuration for all system tables")
    ]

    for table, desc in core_tables:
        cursor.execute("SELECT id FROM table_settings WHERE table_name = ?", (table,))
        if not cursor.fetchone():
            print(f"  Seeding default settings for {table}...")
            # We'll leave settings_json as NULL initially, TableView will handle it
            cursor.execute("""
                INSERT INTO table_settings (table_name, table_description, created_by, updated_by)
                VALUES (?, ?, 1, 1)
            """, (table, desc))

    conn.commit()
    conn.close()
    print("Migration 009_create_table_settings complete.")

if __name__ == "__main__":
    migrate()
