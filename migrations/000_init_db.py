# migrations/000_init_db.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customId TEXT,
            name TEXT,
            username TEXT,
            password TEXT,
            email TEXT,
            display_photo TEXT,
            access_level INTEGER,
            account_status TEXT,
            is_locked BOOLEAN,
            temporary_password TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # SETTINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT,
            setting_value TEXT,
            setting_options TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # NAVIGATIONS (Updated to match your JSON structure 1:1)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS navigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_name TEXT,
            navigation TEXT DEFAULT NULL,
            controller TEXT DEFAULT NULL,
            navigation_type TEXT DEFAULT NULL,      -- "menu", "menu_header"
            navigation_order INTEGER DEFAULT 0,
            parent_id INTEGER DEFAULT NULL,

            -- NEW FIELDS (from your JSON)
            icon TEXT DEFAULT NULL,
            tooltip TEXT DEFAULT NULL,
            is_hidden INTEGER DEFAULT 0,            -- SQLite boolean (0/1)
            status TEXT DEFAULT 'active',

            -- JSON stored as TEXT
            datatable_settings TEXT DEFAULT NULL,

            created_at TEXT DEFAULT NULL,
            updated_at TEXT DEFAULT NULL
        )
    """)

    # ACCESS LEVELS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            access_level_name TEXT,
            access_level_code TEXT,
            "view" TEXT,
            "add" TEXT,
            "edit" TEXT,
            "delete" TEXT,
            "export" TEXT,
            "import" TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Migration 000_init_db complete.")
