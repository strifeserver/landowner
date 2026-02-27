from models.db_config import DB_PATH

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check Merchants
    print("--- Merchants Check ---")
    cursor.execute("SELECT id, shop_name, merchant_service_json, merchant_sheet_id FROM merchants")
    merchants = cursor.fetchall()
    for m in merchants:
        print(f"ID: {m[0]}, Shop: {m[1]}")
        has_json = bool(m[2])
        has_id = bool(m[3])
        print(f"  Service JSON: {'YES' if has_json else 'NO'}")
        print(f"  Sheet ID: {'YES' if has_id else 'NO'}")
        if has_json:
            try:
                json.loads(m[2])
                print("  Service JSON Format: OK")
            except:
                print("  Service JSON Format: INVALID")

    # 3. Check Payments & Merchant ID Check
    print("\n--- Payments & Order Join Check ---")
    from models.Payments import Payments
    from models.Expenses import Expenses
    
    payments = Payments.index()
    print(f"Total Payments: {len(payments)}")
    for p in payments[:3]:
        print(f"Payment ID: {p.id}")
        print(f"  Order ID: {p.order_id}")
        print(f"  Order #: {getattr(p, 'order_number', 'N/A')}")
        print(f"  Customer: {getattr(p, 'customer_name', 'N/A')}")

    print("\n--- Expenses & Order Join Check ---")
    expenses = Expenses.index()
    print(f"Total Expenses: {len(expenses)}")
    for e in expenses[:3]:
        print(f"Expense ID: {e.id}")
        print(f"  Order ID: {e.order_id}")
        print(f"  Order #: {getattr(e, 'order_number', 'N/A')}")
        print(f"  Customer: {getattr(e, 'customer_name', 'N/A')}")

    conn.close()

if __name__ == "__main__":
    check_db()
