from services.GoogleSheetService import GoogleSheetService
import sys

try:
    service = GoogleSheetService()
    # We know there is an order with merchant_id=2 (from previous check)
    success, msg, count = service.sync_unsynced_orders(merchant_id=2)
    print(f"Sync Result: success={success}, msg='{msg}', count={count}")
    
except Exception as e:
    print(f"Error: {e}")
