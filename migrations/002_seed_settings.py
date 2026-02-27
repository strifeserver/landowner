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
            "setting_value": "cms",
            "setting_options": "",
        },
        {
            "id": 2,
            "setting_name": "window_size",
            "setting_value": "1024x768",
            "setting_options": "800x600, 1024x768, 1280x800, 1366x768, 1920x1080",
        },
        {
            "id": 3,
            "setting_name": "navigation_button_size",
            "setting_value": "22",
            "setting_options": "20, 22, 24, 26, 28, 30",
        },
        {
            "id": 4,
            "setting_name": "default_current_logged_in_display_header",
            "setting_value": "cms",
            "setting_options": "",
        },
        {
            "id": 5,
            "setting_name": "default_current_logged_in_sub_header",
            "setting_value": "Admin Panel",
            "setting_options": "",
        },
        {
            "id": 6,
            "setting_name": "default_current_logged_in_image",
            "setting_value": "placeholder_user.png",
            "setting_options": "",
        },
        {
            "id": 7,
            "setting_name": "app_logo",
            "setting_value": "logo.png",
            "setting_options": "",
        },
        {
            "id": 8,
            "setting_name": "app_name",
            "setting_value": "cms",
            "setting_options": "",
        },
        {
            "id": 9,
            "setting_name": "copyright",
            "setting_value": "cms © 2026",
            "setting_options": "",
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
