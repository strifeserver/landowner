import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Tables to skip
    SKIP_TABLES = ['sqlite_sequence']

    for table in tables:
        if table in SKIP_TABLES:
            continue

        print(f"Checking table: {table}")
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        # Add created_by if missing
        if 'created_by' not in columns:
            print(f"  Adding created_by to {table}")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_by INTEGER DEFAULT NULL REFERENCES users(id)")
            except Exception as e:
                print(f"  Error adding created_by to {table}: {e}")

        # Add updated_by if missing
        if 'updated_by' not in columns:
            print(f"  Adding updated_by to {table}")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_by INTEGER DEFAULT NULL REFERENCES users(id)")
            except Exception as e:
                print(f"  Error adding updated_by to {table}: {e}")

        # Add created_at if missing (just in case)
        if 'created_at' not in columns:
            print(f"  Adding created_at to {table}")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_at TEXT DEFAULT NULL")
            except Exception as e:
                print(f"  Error adding created_at to {table}: {e}")

        # Add updated_at if missing (just in case)
        if 'updated_at' not in columns:
            print(f"  Adding updated_at to {table}")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TEXT DEFAULT NULL")
            except Exception as e:
                print(f"  Error adding updated_at to {table}: {e}")

    # Seed existing rows with created_by/updated_by = 1 (System Admin) if they are NULL
    # This assumes ID 1 exists and is a valid user.
    for table in tables:
        if table in SKIP_TABLES: continue
        
        # Only update if the column exists (which we just added)
        try:
             cursor.execute(f"UPDATE {table} SET created_by = 1 WHERE created_by IS NULL")
             cursor.execute(f"UPDATE {table} SET updated_by = 1 WHERE updated_by IS NULL")
             print(f"  Seeded audit fields for {table}")
        except Exception as e:
            print(f"  Could not seed audit fields for {table}: {e}")

    conn.commit()
    conn.close()
    print("Migration 008_add_audit_fields complete.")

if __name__ == "__main__":
    migrate()
