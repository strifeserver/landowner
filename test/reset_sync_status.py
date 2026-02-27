from models.db_config import DB_PATH

def reset_sync_status():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['orders', 'order_items', 'payments', 'expenses']
    
    try:
        total_updated = 0
        for table in tables:
            print(f"Resetting sync status for table: {table}...")
            cursor.execute(f"UPDATE {table} SET spreadsheet_sync = 0")
            count = cursor.rowcount
            print(f"  -> Updated {count} rows in {table}")
            total_updated += count
            
        conn.commit()
        print(f"\nSuccessfully reset spreadsheet_sync to 0 for {total_updated} records across {len(tables)} tables.")
        
    except Exception as e:
        print(f"Error resetting sync status: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_sync_status()
