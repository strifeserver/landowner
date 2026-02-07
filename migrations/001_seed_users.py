# migrations/001_seed_users.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    users = [
        {
            "customId": "000001",
            "name": "Super Admin",
            "username": "admin",
            "password": "admin",
            "email": "admin@admin.com",
            "display_photo": "placeholder_user.png",
            "access_level": 1,
            "account_status": "active",
            "is_locked": False,
            "temporary_password": None,
            "created_at": "2025-06-08 13:52:15",
            "updated_at": "2025-06-08 13:52:15",
        },
        {
            "customId": "000002",
            "name": "Jean Desu",
            "username": "jean",
            "password": "mypassword",
            "email": "admin@admin.com",
            "display_photo": "placeholder_user.png",
            "access_level": 1,
            "account_status": "active",
            "is_locked": False,
            "temporary_password": None,
            "created_at": "2025-06-08 13:52:15",
            "updated_at": "2025-06-08 13:52:15",
        },
        {
            "customId": "000003",
            "name": "Staff Account",
            "username": "staff",
            "password": "staff",
            "email": "admin@admin.com",
            "display_photo": "placeholder_user.png",
            "access_level": 1,
            "account_status": "active",
            "is_locked": False,
            "temporary_password": None,
            "created_at": "2025-06-08 13:52:15",
            "updated_at": "2025-06-08 13:52:15",
        },
        {
            "customId": "000004",
            "name": "Jane Doe",
            "username": "jane_doe",
            "password": "password123",
            "email": "jane@example.com",
            "display_photo": "placeholder_user.png",
            "access_level": 2,
            "account_status": "active",
            "is_locked": False,
            "temporary_password": None,
            "created_at": "2025-06-08 13:55:00",
            "updated_at": "2025-06-08 13:55:00",
        },
    ]

    for user in users:
        cursor.execute(
            """
            INSERT INTO users (
                customId, name, username, password, email, display_photo, access_level,
                account_status, is_locked, temporary_password,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["customId"],
                user["name"],
                user["username"],
                user["password"],
                user["email"],
                user["display_photo"],
                user["access_level"],
                user["account_status"],
                user["is_locked"],
                user["temporary_password"],
                user["created_at"],
                user["updated_at"],
            ),
        )

    conn.commit()
    conn.close()
    print("Seed migration 001_seed_users complete.")


if __name__ == "__main__":
    migrate()
