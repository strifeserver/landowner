import sqlite3
import os

DB_PATH = os.path.join("data", "data.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- Access Levels (Targeted) ---")
cursor.execute("SELECT id, access_level_name, quote(view) FROM access_levels WHERE id=3")
row = cursor.fetchone()
print(f"ID 3: {row}")

# Check ID 1 too
cursor.execute("SELECT id, access_level_name, quote(view) FROM access_levels WHERE id=1")
row = cursor.fetchone()
print(f"ID 1: {row}")

conn.close()
