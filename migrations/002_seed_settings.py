# migrations/002_seed_settings.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    settings_data = [
        {
            "id": 1,
            "setting_name": "App Name",
            "setting_value": "LandOwner",
            "setting_options": "",
        },
        {
            "id": 2,
            "setting_name": "window_size",
            "setting_value": "1024x768",
            "setting_options": "800x600, 1024x768, 1280x800, 1366x768, 1920x1080",
        },
    ]

    for setting in settings_data:
        cursor.execute("""
            INSERT OR REPLACE INTO settings (
                id, setting_name, setting_value, setting_options,
                created_at, updated_at
            ) VALUES (
                :id, :setting_name, :setting_value, :setting_options,
                DATETIME('now'), DATETIME('now')
            )
        """, setting)

    conn.commit()
    conn.close()
    print("Migration 002_seed_settings complete.")

if __name__ == "__main__":
    migrate()
