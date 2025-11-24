import os
import sqlite3
import importlib.util
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "data.db")
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")


def get_migration_files():
    files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.py'))
    return files


def run_migration(file):
    filepath = os.path.join(MIGRATIONS_DIR, file)
    spec = importlib.util.spec_from_file_location("migration", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "migrate"):
        print(f"Running {file}...")
        module.migrate()
        print(f"{file} done.\n")
    else:
        print(f"{file} has no 'migrate()' function. Skipped.\n")


def reset_database():
    if os.path.exists(DB_PATH):
        print(f"Deleting database: {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print("Database does not exist, skipping delete.")


def main():
    # Handle --reset
    if "--reset" in sys.argv:
        print("RESET mode enabled.")
        reset_database()
        print("Database reset completed.\n")

    print("Running migrations...\n")

    for migration in get_migration_files():
        run_migration(migration)

    print("All migrations completed!")


if __name__ == "__main__":
    main()
