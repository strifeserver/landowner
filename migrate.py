import os
import sqlite3
import importlib.util
import sys
# python migrate.py --reset

BASE_DIR = os.path.dirname(__file__)
from models.db_config import DB_PATH
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")


def log_db_state(prefix=""):
    print(f"{prefix}DB PATH       : {DB_PATH}")
    print(f"{prefix}DB EXISTS     : {os.path.exists(DB_PATH)}")
    if os.path.exists(DB_PATH):
        print(f"{prefix}DB FILE SIZE  : {os.path.getsize(DB_PATH)} bytes")
    print("-" * 60)


def get_migration_files():
    files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".py"))
    print(f"Found migrations: {files}")
    print("-" * 60)
    return files


def run_migration(file):
    filepath = os.path.join(MIGRATIONS_DIR, file)

    print(f"Loading migration file: {filepath}")

    spec = importlib.util.spec_from_file_location(file, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "migrate"):
        print(f"Running migration: {file}")
        log_db_state("  ")

        module.migrate()

        print(f"Finished migration: {file}")
        log_db_state("  ")
        print()
    else:
        print(f"{file} has no migrate() function. Skipped.\n")


def reset_database():
    print("RESET DATABASE REQUESTED")
    log_db_state("  BEFORE RESET -> ")

    if os.path.exists(DB_PATH):
        print(f"Deleting database file: {DB_PATH}")
        os.remove(DB_PATH)
        print("Database file deleted.")
    else:
        print("Database file does not exist. Nothing to delete.")

    log_db_state("  AFTER RESET  -> ")
    print()


def main():
    print("=" * 60)
    print("PYTHON SQLITE MIGRATION RUNNER")
    print("=" * 60)

    if "--reset" in sys.argv:
        print("RESET MODE ENABLED")
        reset_database()
    else:
        print("RESET MODE NOT ENABLED")

    print("Starting migration process...\n")

    for migration in get_migration_files():
        run_migration(migration)

    print("=" * 60)
    print("ALL MIGRATIONS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
