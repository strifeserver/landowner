import os
import sqlite3
import importlib.util

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
        print(f"{file} done.")
    else:
        print(f"{file} has no 'migrate()' function. Skipped.")

def main():
    for migration in get_migration_files():
        run_migration(migration)

if __name__ == "__main__":
    main()
