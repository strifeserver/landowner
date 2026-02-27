import sqlite3
import os
import json

DB_PATH = os.path.join("data", "data.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM table_settings")
cols = [description[0] for description in cursor.description]
rows = cursor.fetchall()

for row in rows:
    data = dict(zip(cols, row))
    print(f"ID: {data['id']}, Table: {data['table_name']}")
    print(f"Settings JSON: {data['settings_json']}")
    print("-" * 20)

conn.close()
