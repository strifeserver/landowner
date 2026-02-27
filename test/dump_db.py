import sqlite3
import os

DB_PATH = os.path.join("data", "data.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- Access Levels ---")
cursor.execute("SELECT id, access_level_name, view FROM access_levels")
for row in cursor.fetchall():
    print(row)

print("\n--- Navigations ---")
cursor.execute("SELECT id, menu_name FROM navigations")
for row in cursor.fetchall():
    print(row)

conn.close()
