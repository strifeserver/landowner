# migrations/003_seed_navigations.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    navigations = [
        {
            "id": 1,
            "menu_name": "Dashboard",
            "navigation": "dashboard",
            "controller": "DashboardsController",
            "pagination": True,
            "items_per_page": 5,
        },
        {
            "id": 2,
            "menu_name": "Users Management",
            "navigation": "users",
            "controller": "UsersController",
            "pagination": True,
            "items_per_page": 10,
        },
        {
            "id": 3,
            "menu_name": "Tenant Management",
            "navigation": "tenant_management",
            "controller": "TenantsController",
            "pagination": True,
            "items_per_page": 5,
        },
        {
            "id": 4,
            "menu_name": "Settings",
            "navigation": "settings",
            "controller": "SettingsController",
            "pagination": True,
            "items_per_page": 5,
        },
    ]

    for nav in navigations:
        cursor.execute("""
            INSERT INTO navigations (
                id, menu_name, navigation, controller,
                pagination, items_per_page,
                created_at, updated_at
            ) VALUES (
                :id, :menu_name, :navigation, :controller,
                :pagination, :items_per_page,
                DATETIME('now'), DATETIME('now')
            )
        """, nav)

    conn.commit()
    conn.close()
    print("Migration 003_seed_navigations complete.")

if __name__ == "__main__":
    migrate()
