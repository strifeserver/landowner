# run_migrations.py
import sys
import os
import importlib.util

def run_migration(file_path):
    print(f"Running migration: {os.path.basename(file_path)}...")
    spec = importlib.util.spec_from_file_location("migration", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, 'migrate'):
        module.migrate()
    else:
        print(f"Warning: {os.path.basename(file_path)} does not have a migrate() function.")

def main():
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    
    # Define migration order
    migration_files = [
        "000_init_db.py",           # 1. Create Tables
        "001_seed_users.py",        # 2. Seed Users
        "002_seed_settings.py",     # 3. Seed Settings
        "003_seed_navigations.py",  # 4. Seed Navigations
        "004_seed_access_levels.py",# 5. Seed Access Levels
        "005_add_permissions_to_access_levels.py", # 6. Set initial permissions
        "006_create_crud_definitions.py",          # 7. Metadata for CRUD
        "007_update_users_table.py",               # 8. Schema updates (if any missed)
    ]

    for filename in migration_files:
        path = os.path.join(migrations_dir, filename)
        if os.path.exists(path):
            run_migration(path)
        else:
            print(f"Error: Migration file not found: {path}")

    print("\nCheckpoint Complete! Database initialized and seeded successfully.")

if __name__ == "__main__":
    main()
