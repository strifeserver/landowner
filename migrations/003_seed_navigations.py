# migrations/003_seed_navigations.py

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    navigations = [
        {
            "id": 1,
            "menu_name": "Dashboard",
            "navigation_order": 1,
            "navigation": "dashboard",
            "navigation_type": "menu",
            "parent_id": None,
            "controller": "DashboardsController",
            "datatable_settings": {
                "is_paginated": True,
                "items_per_page": 10,
            },
            "icon": None,
            "tooltip": "",
            "is_hidden": False,
            "status": "active",
        },
        {
            "id": 2,
            "menu_name": "Users Management",
            "navigation_order": 2,
            "navigation": "users",
            "navigation_type": "menu",
            "parent_id": None,
            "controller": "UsersController",
            "datatable_settings": {
                "is_paginated": True,
                "items_per_page": 10,
            },
            "icon": None,
            "tooltip": "",
            "is_hidden": False,
            "status": "active",
        },
        {
            "id": 3,
            "menu_name": "Tenant Management",
            "navigation_order": 3,
            "navigation": "tenant_management",
            "navigation_type": "menu",
            "parent_id": None,
            "controller": "TenantsController",
            "datatable_settings": {
                "is_paginated": True,
                "items_per_page": 10,
            },
            "icon": None,
            "tooltip": "",
            "is_hidden": False,
            "status": "active",
        },
        {
            "id": 4,
            "menu_name": "Admin Tools",
            "navigation_order": 4,
            "navigation": None,
            "navigation_type": "menu_header",
            "parent_id": None,
            "controller": None,
            "datatable_settings": None,
            "icon": None,
            "tooltip": "",
            "is_hidden": False,
            "status": "active",
        },
        {
            "id": 5,
            "menu_name": "Settings",
            "navigation_order": 5,
            "navigation": "settings",
            "navigation_type": "menu",
            "parent_id": None,
            "controller": "SettingsController",
            "datatable_settings": {
                "is_paginated": True,
                "items_per_page": 10,
            },
            "icon": None,
            "tooltip": "",
            "is_hidden": False,
            "status": "active",
        },
    ]

    for nav in navigations:
        # Convert dict to JSON string (or keep None)
        datatable_json = json.dumps(nav["datatable_settings"]) if nav["datatable_settings"] else None

        cursor.execute(
            """
            INSERT INTO navigations (
                id, menu_name, navigation_order, navigation, navigation_type,
                parent_id, controller, datatable_settings,
                icon, tooltip, is_hidden, status,
                created_at, updated_at
            ) VALUES (
                :id, :menu_name, :navigation_order, :navigation, :navigation_type,
                :parent_id, :controller, :datatable_settings,
                :icon, :tooltip, :is_hidden, :status,
                DATETIME('now'), DATETIME('now')
            )
            """,
            {
                "id": nav["id"],
                "menu_name": nav["menu_name"],
                "navigation_order": nav["navigation_order"],
                "navigation": nav["navigation"],
                "navigation_type": nav["navigation_type"],
                "parent_id": nav["parent_id"],
                "controller": nav["controller"],
                "datatable_settings": datatable_json,
                "icon": nav["icon"],
                "tooltip": nav["tooltip"],
                "is_hidden": nav["is_hidden"],
                "status": nav["status"],
            }
        )

    conn.commit()
    conn.close()
    print("Migration 003_seed_navigations complete.")

if __name__ == "__main__":
    migrate()
