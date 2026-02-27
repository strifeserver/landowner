import os
import sqlite3
import json
import logging
from models.Setting import Setting
from models.db_config import DB_PATH

class GoogleSheetService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_credentials(self, service_json=None, sheet_id=None):
        """Fetch credentials from settings table or use provided values."""
        try:
            # 1. Use provided service_json or fetch from settings
            if service_json:
                try:
                    service_account_info = json.loads(service_json)
                except json.JSONDecodeError:
                    return None, "Invalid JSON in provided Service JSON."
            else:
                sa_settings = Setting.index(filters={"setting_name": "google_service_account"})
                if not sa_settings or not sa_settings[0].setting_value:
                    return None, "google_service_account setting not found or empty."
                try:
                    service_account_info = json.loads(sa_settings[0].setting_value)
                except json.JSONDecodeError:
                    return None, "Invalid JSON in google_service_account setting."

            # 2. Use provided sheet_id or fetch from settings
            if not sheet_id:
                id_settings = Setting.index(filters={"setting_name": "google_sheet_id"})
                if not id_settings or not id_settings[0].setting_value:
                    return None, "google_sheet_id setting not found or empty."
                sheet_id = id_settings[0].setting_value

            return {
                "service_account": service_account_info,
                "sheet_id": sheet_id
            }, None
        except Exception as e:
            return None, f"Error fetching settings: {str(e)}"

    def validate_connection(self, service_json=None, sheet_id=None):
        """
        Validates Google Sheets connection:
        1. Loads credentials (from args or settings)
        2. Authenticates
        3. Tests Read
        4. Tests Write
        """
        creds_data, error = self.get_credentials(service_json, sheet_id)
        if error:
            return {"success": False, "message": error}

        try:
            # We use google-auth and google-api-python-client
            # If not installed, we'll suggest installing them
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
            except ImportError:
                return {
                    "success": False, 
                    "message": "Required libraries not found. Please run: pip install google-auth google-api-python-client"
                }

            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Authenticate
            creds = service_account.Credentials.from_service_account_info(
                creds_data["service_account"], scopes=SCOPES
            )
            
            service = build('sheets', 'v4', credentials=creds)
            spreadsheet_id = creds_data["sheet_id"]

            # 1. Test Read Access
            try:
                sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheet_name = sheet_metadata.get('properties', {}).get('title', 'Unknown Sheet')
                read_ok = True
            except Exception as e:
                return {"success": False, "message": f"Read Access Failed: {str(e)}"}

            # 2. Test Write Access
            # We'll try to write to a dummy range (e.g. 'Properties!Z999' or a new sheet)
            # Better to just try updating a specific cell and then clearing it if possible, 
            # but we don't want to mess up the user's data.
            # We'll try to append a row to a sheet named 'cms_Test' or just use the first sheet's A1 if it's empty?
            # Safer: just check if we can update the title or something? 
            # No, let's try to append a value to a hidden range.
            
            test_range = 'A1:A1' # Risk: overwriting A1. 
            # Let's try to get the first sheet name
            sheets = sheet_metadata.get('sheets', [])
            if not sheets:
                return {"success": False, "message": "No sheets found in the spreadsheet."}
            
            first_sheet_name = sheets[0].get('properties', {}).get('title', 'Sheet1')
            test_range = f"'{first_sheet_name}'!Z100" # Use a far-off cell
            
            try:
                # 1. Write Z100
                value_input_option = 'RAW'
                value_range_body = {
                    'values': [['Connection Test']]
                }
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=test_range,
                    valueInputOption=value_input_option, body=value_range_body).execute()
                
                # 2. Clear Z100
                service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id, range=test_range).execute()
                
                write_ok = True
            except Exception as e:
                return {
                    "success": True, 
                    "read_status": "OK",
                    "write_status": "FAILED",
                    "message": f"Connected to '{sheet_name}'. Read OK, but Write Failed: {str(e)}"
                }

            return {
                "success": True,
                "read_status": "OK",
                "write_status": "OK",
                "sheet_name": sheet_name,
                "message": f"Successfully connected to '{sheet_name}'. Read and Write access confirmed."
            }

        except Exception as e:
            return {"success": False, "message": f"Connection Error: {str(e)}"}

    def get_service(self, service_json=None, sheet_id=None):
        """Get authenticated Google Sheets API service."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            raise Exception("Required libraries not found. Please run: pip install google-auth google-api-python-client")

        creds_data, error = self.get_credentials(service_json, sheet_id)
        if error:
            raise Exception(error)

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_info(
            creds_data["service_account"], scopes=SCOPES
        )
        
        service = build('sheets', 'v4', credentials=creds)
        return service, creds_data["sheet_id"]

    def ensure_users_sheet(self):
        """
        Ensure 'Users' sheet exists in the spreadsheet.
        If not, create it with headers: id, customId, username, email, last_login
        Returns: (success, message)
        """
        try:
            service, spreadsheet_id = self.get_service()
            
            # Get all sheets
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # Check if 'Users' sheet exists
            users_sheet_exists = any(
                sheet.get('properties', {}).get('title', '').lower() == 'users' 
                for sheet in sheets
            )
            
            if not users_sheet_exists:
                # Create 'Users' sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': 'Users'
                        }
                    }
                }]
                
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                
                # Add headers
                headers = [['id', 'customId', 'username', 'email', 'last_login']]
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='Users!A1:E1',
                    valueInputOption='RAW',
                    body={'values': headers}
                ).execute()
                
                return True, "Users sheet created successfully"
            
            return True, "Users sheet already exists"
            
        except Exception as e:
            return False, f"Error ensuring Users sheet: {str(e)}"

    def sync_user_to_sheet(self, user):
        """
        Sync user data to Google Sheets.
        If user exists (by id), update the row. Otherwise, append new row.
        Args:
            user: User object with id, customId, username, email, last_login
        Returns: (success, message)
        """
        try:
            # Ensure sheet exists
            success, msg = self.ensure_users_sheet()
            if not success:
                return False, msg
            
            service, spreadsheet_id = self.get_service()
            
            # Get all data from Users sheet
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Users!A:E'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                # No data, add headers and user
                headers = [['id', 'customId', 'username', 'email', 'last_login']]
                user_row = [[
                    str(user.id),
                    str(user.customId or ''),
                    str(user.username or ''),
                    str(user.email or ''),
                    str(getattr(user, 'last_login', '') or '')
                ]]
                
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='Users!A1:E2',
                    valueInputOption='RAW',
                    body={'values': headers + user_row}
                ).execute()
                
                return True, "User added to sheet"
            
            # Find user row by id (column A)
            user_id_str = str(user.id)
            row_index = None
            
            for i, row in enumerate(values):
                if i == 0:  # Skip header
                    continue
                if row and len(row) > 0 and str(row[0]) == user_id_str:
                    row_index = i + 1  # 1-indexed
                    break
            
            user_data = [
                str(user.id),
                str(user.customId or ''),
                str(user.username or ''),
                str(user.email or ''),
                str(getattr(user, 'last_login', '') or '')
            ]
            
            if row_index:
                # Update existing row
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'Users!A{row_index}:E{row_index}',
                    valueInputOption='RAW',
                    body={'values': [user_data]}
                ).execute()
                return True, f"User updated in sheet (row {row_index})"
            else:
                # Append new row
                service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range='Users!A:E',
                    valueInputOption='RAW',
                    body={'values': [user_data]}
                ).execute()
                return True, "User added to sheet"
                
        except Exception as e:
            return False, f"Error syncing user to sheet: {str(e)}"

    def update_user_login_date(self, user_id):
        """
        Updates the last_login timestamp for a user in the Google Sheet.
        Only succeeds if the user already exists in the sheet.
        Returns: (success, message)
        """
        try:
            from datetime import datetime
            service, spreadsheet_id = self.get_service()
            
            # 1. Get current values to find the user
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Users!A:A' # Only need IDs to find the row
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return False, "User validation sheet is empty."
            
            user_id_str = str(user_id)
            row_index = None
            for i, row in enumerate(values):
                if row and str(row[0]) == user_id_str:
                    row_index = i + 1
                    break
            
            if not row_index:
                return False, f"User ID {user_id} not found in validation spreadsheet."
            
            # 2. Update ONLY the last_login column (Column E)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'Users!E{row_index}',
                valueInputOption='USER_ENTERED',
                body={'values': [[now]]}
            ).execute()
            
            return True, f"User validation timestamp updated in sheet (row {row_index})."
            
        except Exception as e:
            return False, f"Spreadsheet validation error: {str(e)}"

    def ensure_sheet(self, sheet_name, headers, service_json=None, sheet_id=None):
        """
        Ensure a specific sheet exists. If not, create it and add headers.
        """
        try:
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            
            # Get all sheets
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # Check if sheet exists
            sheet_exists = any(
                sheet.get('properties', {}).get('title', '').lower() == sheet_name.lower() 
                for sheet in sheets
            )
            
            if not sheet_exists:
                # Create sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
                
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                
                # Add headers
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'{sheet_name}!A1',
                    valueInputOption='USER_ENTERED',
                    body={'values': [headers]}
                ).execute()
                
                return True, f"Sheet '{sheet_name}' created."
            
            return True, f"Sheet '{sheet_name}' exists."
            
        except Exception as e:
            return False, f"Error ensuring sheet '{sheet_name}': {str(e)}"

    def append_data(self, sheet_name, values, service_json=None, sheet_id=None):
        """
        Append rows to a sheet.
        values: List of lists (rows)
        """
        try:
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'!A:A",
                valueInputOption='USER_ENTERED',
                body={'values': values}
            ).execute()
            
            return True, "Data appended successfully."
        except Exception as e:
            return False, f"Error appending data to '{sheet_name}': {str(e)}"

    def get_sheet_id_map(self, sheet_name, service_json=None, sheet_id=None):
        """
        Helper to get a map of {id: row_number} from a sheet.
        Returns: (id_to_row_map, id_col_index)
        """
        try:
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            read_result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'"
            ).execute()
            values = read_result.get('values', [])
            if not values:
                return {}, -1
            
            headers = [h.strip().lower() for h in values[0]]
            id_col_idx = -1
            if 'id' in headers:
                id_col_idx = headers.index('id')
            
            id_to_row = {}
            if id_col_idx >= 0:
                for r_idx, r_val in enumerate(values):
                    if len(r_val) > id_col_idx:
                        id_to_row[str(r_val[id_col_idx])] = r_idx + 1
            return id_to_row, id_col_idx
        except Exception as e:
            return {}, -1

    def update_or_append_data(self, sheet_name, values, record_id, id_col_idx, id_to_row, service_json=None, sheet_id=None, google_row_index=None):
        """
        Updates a row if record_id exists in id_to_row, otherwise appends.
        Returns: (success, message, row_number)
        """
        try:
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            row_num = None
            
            # Prioritize google_row_index if available
            if google_row_index and str(google_row_index).isdigit() and int(google_row_index) > 0:
                row_num = int(google_row_index)
            else:
                row_num = id_to_row.get(str(record_id))
            
            if row_num:
                # UPDATE
                # We update the row starting from column A
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!A{row_num}",
                    valueInputOption='USER_ENTERED',
                    body={'values': values}
                ).execute()
                return True, "Data updated successfully.", row_num
            else:
                # APPEND
                result = service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!A:A",
                    valueInputOption='USER_ENTERED',
                    body={'values': values},
                    includeValuesInResponse=False  # We just need the updates
                ).execute()
                
                # Extract new row number from updatedRange
                # Format: "Sheet1!A10:Z10"
                new_row_num = 0
                updated_range = result.get('updates', {}).get('updatedRange')
                if updated_range:
                    try:
                        # Split by '!' then take the part after (e.g., A10:Z10)
                        # Then take the first digits found
                        import re
                        match = re.search(r'!A(\d+)', updated_range)
                        if match:
                             new_row_num = int(match.group(1))
                        else:
                             # Fallback regex just in case col isn't A
                             match = re.search(r'![A-Z]+(\d+)', updated_range)
                             if match:
                                 new_row_num = int(match.group(1))
                    except:
                        pass
                
                return True, "Data appended successfully.", new_row_num
        except Exception as e:
            return False, f"Error in update_or_append to '{sheet_name}': {str(e)}", 0

    def merge_cells(self, sheet_name, start_row, end_row, start_col, end_col, service_json=None, sheet_id=None):
        """
        Merge cells in a specific range.
        row and col are 0-indexed.
        """
        try:
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            
            # 1. Get sheetId (numerical) for the sheet name
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            target_sheet_id = None
            for sheet in sheets:
                if sheet.get('properties', {}).get('title', '').lower() == sheet_name.lower():
                    target_sheet_id = sheet.get('properties', {}).get('sheetId')
                    break
            
            if target_sheet_id is None:
                return False, f"Sheet '{sheet_name}' not found for merging."

            requests = [{
                'mergeCells': {
                    'range': {
                        'sheetId': target_sheet_id,
                        'startRowIndex': start_row,
                        'endRowIndex': end_row + 1,
                        'startColumnIndex': start_col,
                        'endColumnIndex': end_col + 1
                    },
                    'mergeType': 'MERGE_ALL'
                }
            }]
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            return True, "Cells merged successfully."
        except Exception as e:
            return False, f"Error merging cells: {str(e)}"

    def get_user_last_login_from_sheet(self, user_id):
        """
        Get user's last_login from Google Sheets.
        Args:
            user_id: User ID to look up
        Returns: last_login timestamp string or None
        """
        try:
            service, spreadsheet_id = self.get_service()
            
            # Get all data from Users sheet
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Users!A:E'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) < 2:  # No data or only headers
                return None
            
            # Find user row by id (column A)
            user_id_str = str(user_id)
            
            for i, row in enumerate(values):
                if i == 0:  # Skip header
                    continue
                if row and len(row) > 0 and str(row[0]) == user_id_str:
                    # last_login is in column E (index 4)
                    if len(row) > 4 and row[4]:
                        return row[4]
                    return None
            
            return None  # User not found
            
        except Exception as e:
            self.logger.error(f"Error getting user last_login from sheet: {str(e)}")
            return None

    def get_sync_settings(self, table_name):
        """
        Fetch sync settings for a table.
        Returns: (headers, db_columns) or (None, None)
        """
        try:
            from models.sheet_sync_settings import SheetSyncSettings
            import json
            
            record = SheetSyncSettings.find_by_table(table_name)
            if not record or not record[2]:
                return None, None
                
            settings = json.loads(record[2])
            # Filter valid synced columns and sort
            synced_cols = [c for c in settings if c.get('sync', True)]
            synced_cols.sort(key=lambda x: x.get('order', 999))
            
            headers = [c['name'].replace('_', ' ').title() for c in synced_cols]
            db_columns = [c['name'] for c in synced_cols]
            
            # Ensure 'id' is always selected to update status, but maybe not synced?
            # Actually we usually sync ID as first col.
            
            return headers, db_columns
        except Exception as e:
            # Silently fail or log to file if needed
            return None, None

    def sync_unsynced_orders(self, merchant_id=None, sync_all=False, service_json=None, sheet_id=None):
        """
        Syncs orders to Google Sheets.
        If sync_all is True, syncs ALL orders regardless of spreadsheet_sync status.
        Otherwise, only syncs unsynced orders.
        After successful sync, updates spreadsheet_sync = 1.
        Returns: (success, message, synced_count)
        """
        try:
            from models.Orders import Orders
            import sqlite3
            import os
            
            # Get unsynced orders
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for custom settings
            custom_headers, custom_cols = self.get_sync_settings('orders')
            
            if custom_headers:
                # Build dynamic query
                cols_str = ", ".join(custom_cols)
                # Ensure we select google_row_index at the end
                query = f"SELECT id, {cols_str}, google_row_index FROM orders WHERE 1=1"
                headers = custom_headers
            else:
                # Explicitly list columns to sync, excluding google_row_index from the sync data
                db_cols = ['id', 'order_number', 'customer_name', 'customer_id', 'order_status', 'payment_status', 
                           'shipping_reference_link', 'shipping_reference_number', 'shipping_notes', 'order_notes', 'merchant_id', 
                           'sub_total_amount', 'discount_amount', 'shipping_fee', 'total_amount', 'ordered_at', 'customer_location', 
                           'spreadsheet_sync', 'created_at', 'updated_at', 'created_by', 'updated_by']
                
                cols_str = ", ".join(db_cols)
                query = f"SELECT {cols_str}, google_row_index FROM orders WHERE 1=1"
                
                # Define default headers
                headers = ['ID', 'Order Number', 'Customer Name', 'Customer ID', 'Order Status', 'Payment Status', 
                           'Shipping Ref Link', 'Shipping Ref Number', 'Shipping Notes', 'Order Notes', 'Merchant ID', 
                           'Sub Total', 'Discount', 'Shipping Fee', 'Total Amount', 'Ordered At', 'Customer Location', 
                           'Spreadsheet Sync', 'Created At', 'Updated At', 'Created By', 'Updated By']

            params = []
            
            if not sync_all:
                query += " AND (spreadsheet_sync = 0 OR spreadsheet_sync IS NULL)"
            
            if merchant_id:
                query += " AND merchant_id = ?"
                params.append(merchant_id)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Ensure 'Orders' sheet exists
            ok, msg = self.ensure_sheet('Orders', headers, service_json, sheet_id)
            if not ok:
                conn.close()
                return False, msg, 0

            if not rows:
                conn.close()
                return True, "No unsynced orders found", 0
            
            # Sync to Google Sheets
                
            # Fetch existing data for duplicate check ONLY if we have rows without google_row_index
            # Optimization: Check if any row needs id_to_row mapping
            needs_sheet_map = False
            for row in rows:
                g_index = row[-1]
                if not g_index:
                    needs_sheet_map = True
                    break
            
            id_to_row = {}
            id_col_idx = -1
            
            if needs_sheet_map:
                id_to_row, id_col_idx = self.get_sheet_id_map('Orders', service_json, sheet_id)

            synced_count = 0
            for row in rows:
                order_id = row[0]
                g_index = row[-1]
                
                # Prepare data for push (exclude last col which is google_row_index)
                if custom_headers:
                    # id is first, then custom cols, then google_row_index
                    # row_data should be row[1:-1]
                    row_data = [val if val is not None else '' for val in row[1:-1]]
                else:
                    # db_cols (including id), then google_row_index
                    # row_data should be row[:-1]
                    row_data = [val if val is not None else '' for val in row[:-1]]

                ok, msg, new_row_num = self.update_or_append_data('Orders', [row_data], order_id, id_col_idx, id_to_row, service_json, sheet_id, google_row_index=g_index)
                    
                if ok:
                    updates = ["spreadsheet_sync = 1"]
                    params = []
                    if new_row_num:
                        updates.append("google_row_index = ?")
                        params.append(new_row_num)
                    
                    params.append(order_id)
                    cursor.execute(f"UPDATE orders SET {', '.join(updates)} WHERE id = ?", params)
                    synced_count += 1
            
            conn.commit()
            conn.close()
            
            return True, f"Successfully synced {synced_count} orders", synced_count
        except Exception as e:
            return False, f"Error syncing orders: {str(e)}", 0

    def sync_unsynced_order_items(self, order_id=None, sync_all=False, service_json=None, sheet_id=None, merchant_id=None):
        """
        Syncs order items. If sync_all is True, ignores spreadsheet_sync status.
        Returns: (success, message, synced_count)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for custom settings
            custom_headers, custom_cols = self.get_sync_settings('order_items')
            
            if custom_headers:
                # Order Items needs joins for customer_name, etc.
                # Supported joined fields: customer_name, customer_location
                
                select_parts = []
                for col in custom_cols:
                    if col in ['customer_name', 'customer_location']:
                        select_parts.append(f"o.{col}")
                    elif col == 'downpayment':
                        # Sum of payments for this order
                        select_parts.append(f"(SELECT COALESCE(SUM(amount_paid), 0) FROM payments WHERE order_id = oi.order_id) as downpayment")
                    elif col == 'remaining_balance':
                        # (Sum of item prices) - (Sum of payments)
                        select_parts.append(f"((SELECT COALESCE(SUM(quantity * price), 0) FROM order_items WHERE order_id = oi.order_id) - (SELECT COALESCE(SUM(amount_paid), 0) FROM payments WHERE order_id = oi.order_id)) as remaining_balance")
                    elif col in ['id', 'order_id', 'order_number', 'item_name', 'quantity', 'scale', 'item_notes', 'item_status', 'price', 'spreadsheet_sync', 'created_at', 'updated_at', 'created_by', 'updated_by']:
                        select_parts.append(f"oi.{col}")
                    else:
                        select_parts.append(f"oi.{col}") # Default to order_items table

                cols_str = ", ".join(select_parts)
                # Ensure google_row_index is selected
                query = f"SELECT oi.id, {cols_str}, oi.google_row_index FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.id WHERE 1=1"
                headers = custom_headers
            else:
                db_cols = ['id', 'order_id', 'order_number', 'item_name', 'quantity', 'scale', 
                           'item_notes', 'item_status', 'price', 'spreadsheet_sync', 'created_at', 'updated_at', 'created_by', 'updated_by']
                
                select_parts = [f"oi.{col}" for col in db_cols]
                cols_str = ", ".join(select_parts)
                query = f"SELECT {cols_str}, oi.google_row_index FROM order_items oi WHERE 1=1"
                
                # Define default headers
                headers = ['ID', 'Order ID', 'Order Number', 'Item Name', 'Quantity', 'Scale', 
                           'Item Notes', 'Item Status', 'Price', 'Spreadsheet Sync', 'Created At', 'Updated At', 'Created By', 'Updated By']

            params = []
            
            if not sync_all:
                query += " AND (oi.spreadsheet_sync = 0 OR oi.spreadsheet_sync IS NULL)"
            
            if order_id:
                query += " AND oi.order_id = ?"
                params.append(order_id)
            
            if merchant_id:
                query += " AND o.merchant_id = ?"
                params.append(merchant_id)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Ensure 'OrderItems' sheet exists
            ok, msg = self.ensure_sheet('OrderItems', headers, service_json, sheet_id)
            if not ok:
                 conn.close()
                 return False, msg, 0

            if not rows:
                conn.close()
                return True, "OrderItems sheet checked. No new items to sync.", 0
            
            # Track last order_id processed to merge cells if needed
            last_order_id = None
            block_start_row = -1
            merge_ranges = [] # List of (start_row, end_row)
            
            # CRITICAL: We need to know the LAST ROW's Order Number from the Google Sheet itself.
            try:
                check_col_idx = -1
                if custom_headers:
                    if 'order_number' in custom_cols:
                        check_col_idx = custom_cols.index('order_number')
                    elif 'order_id' in custom_cols:
                        check_col_idx = custom_cols.index('order_id')
                else:
                    check_col_idx = 2 
                
                if check_col_idx >= 0:
                    service, spreadsheet_id = self.get_service(service_json, sheet_id)
                    read_result = service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range='OrderItems' 
                    ).execute()
                    
                    existing_values = read_result.get('values', [])
                    id_to_row = {}
                    id_col_idx = -1
                    if existing_values:
                        headers_in_sheet = [h.strip().lower() for h in existing_values[0]]
                        if 'id' in headers_in_sheet:
                            id_col_idx = headers_in_sheet.index('id')
                            for r_idx, r_val in enumerate(existing_values):
                                if len(r_val) > id_col_idx:
                                    id_to_row[str(r_val[id_col_idx])] = r_idx + 1

                    if existing_values and len(existing_values) > 1:
                        last_row = existing_values[-1]
                        if len(last_row) > check_col_idx:
                            last_order_id = last_row[check_col_idx]
                            
                            # Find start of this order block in existing sheet
                            for i in range(len(existing_values)-1, 0, -1):
                                row_data_prev = existing_values[i]
                                if len(row_data_prev) > check_col_idx and str(row_data_prev[check_col_idx]) == str(last_order_id):
                                    block_start_row = i
                                else:
                                    break
            except Exception as e:
                pass
            
            # Keep track of current row in the sheet
            current_sheet_row = len(existing_values) if 'existing_values' in locals() else 1 
            
            # Ensure id_to_row and id_col_idx are defined even if exception occurred
            if 'id_to_row' not in locals(): id_to_row = {}
            if 'id_col_idx' not in locals(): id_col_idx = -1

            synced_count = 0
            for row in rows:
                item_id = row[0]
                g_index = row[-1]
                
                if custom_headers:
                    # row is (id, cols..., google_row_index)
                    # row_data should be row[1:-1]
                    row_data = [val if val is not None else '' for val in row[1:-1]]
                    
                    current_order_val = None
                    order_col_idx = -1
                    
                    if 'order_number' in custom_cols:
                        order_col_idx = custom_cols.index('order_number')
                    elif 'order_id' in custom_cols:
                        order_col_idx = custom_cols.index('order_id')
                        
                    if order_col_idx >= 0:
                        current_order_val = row_data[order_col_idx]
                        
                        if str(current_order_val) == str(last_order_id):
                            if block_start_row == -1:
                                block_start_row = current_sheet_row - 1
                            pass
                        else:
                            block_start_row = current_sheet_row
                            
                        last_order_id = current_order_val
                else:
                    # row is (col1, col2..., google_row_index)
                    # row_data should be row[:-1]
                    row_data = [val if val is not None else '' for val in row[:-1]]

                ok, msg, new_row_num = self.update_or_append_data('OrderItems', [row_data], item_id, id_col_idx, id_to_row, service_json, sheet_id, google_row_index=g_index)
                
                if ok:
                    updates = ["spreadsheet_sync = 1"]
                    params = []
                    if new_row_num:
                         updates.append("google_row_index = ?")
                         params.append(new_row_num)
                    
                    params.append(item_id)
                    cursor.execute(f"UPDATE order_items SET {', '.join(updates)} WHERE id = ?", params)
                    synced_count += 1
                    current_sheet_row += 1
            
            conn.commit()
            
            # FINAL STEP: Apply Merges
            # We need to re-scan the rows we just added or use the logic above.
            # Let's re-fetch the sheet state to be absolutely sure of row indices
            try:
                if synced_count > 0:
                     service, spreadsheet_id = self.get_service(service_json, sheet_id)
                     read_result = service.spreadsheets().values().get(
                         spreadsheetId=spreadsheet_id,
                         range='OrderItems' 
                     ).execute()
                     all_values = read_result.get('values', [])
                     
                     if all_values and len(all_values) > 2:
                         last_val = None
                         start_idx = -1
                         
                         dp_col = -1
                         rb_col = -1
                         if custom_headers:
                             if 'downpayment' in custom_cols: dp_col = custom_cols.index('downpayment')
                             if 'remaining_balance' in custom_cols: rb_col = custom_cols.index('remaining_balance')
                         
                         if dp_col >= 0 or rb_col >= 0:
                             sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                             sheets = sheet_metadata.get('sheets', [])
                             target_sheet_id = None
                             for sheet in sheets:
                                 if sheet.get('properties', {}).get('title', '').lower() == 'OrderItems'.lower():
                                     target_sheet_id = sheet.get('properties', {}).get('sheetId')
                                     break
                             
                             if target_sheet_id is not None:
                                 merge_requests = []
                                 def add_merge_request(r1, r2, c1, c2):
                                     merge_requests.append({
                                         'mergeCells': {
                                             'range': {
                                                 'sheetId': target_sheet_id,
                                                 'startRowIndex': r1,
                                                 'endRowIndex': r2 + 1,
                                                 'startColumnIndex': c1,
                                                 'endColumnIndex': c2 + 1
                                             },
                                             'mergeType': 'MERGE_ALL'
                                         }
                                     })

                                 for i in range(1, len(all_values)):
                                     row = all_values[i]
                                     current_val = row[check_col_idx] if len(row) > check_col_idx else None
                                     
                                     if current_val == last_val and current_val is not None:
                                         if start_idx == -1:
                                             start_idx = i - 1
                                     else:
                                         if start_idx != -1:
                                             if dp_col >= 0: add_merge_request(start_idx, i-1, dp_col, dp_col)
                                             if rb_col >= 0: add_merge_request(start_idx, i-1, rb_col, rb_col)
                                             start_idx = -1
                                     last_val = current_val
                                 
                                 if start_idx != -1:
                                     i = len(all_values)
                                     if dp_col >= 0: add_merge_request(start_idx, i-1, dp_col, dp_col)
                                     if rb_col >= 0: add_merge_request(start_idx, i-1, rb_col, rb_col)
                                 
                                 if merge_requests:
                                     service.spreadsheets().batchUpdate(
                                         spreadsheetId=spreadsheet_id,
                                         body={'requests': merge_requests}
                                     ).execute()
            except Exception as e:
                print(f"Merge error: {e}")
            
            conn.close()
            
            return True, f"Successfully synced {synced_count} order items", synced_count
        except Exception as e:
            return False, f"Error syncing order items: {str(e)}", 0

    def sync_unsynced_payments(self, order_id=None, sync_all=False, service_json=None, sheet_id=None, merchant_id=None):
        """
        Syncs payments. If sync_all is True, ignores spreadsheet_sync status.
        Returns: (success, message, synced_count)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for custom settings
            custom_headers, custom_cols = self.get_sync_settings('payments')
            
            if custom_headers:
                # Payments needs joins for customer_name, etc.
                # Supported joined fields: customer_name, customer_location, order_number
                # We need to build the SELECT list carefully.
                
                select_parts = []
                for col in custom_cols:
                    if col in ['customer_name', 'customer_location', 'order_number']:
                        select_parts.append(f"o.{col}")
                    elif col in ['id', 'order_id', 'merchant_id', 'payment_reference', 'amount_paid', 'payment_status', 'paid_at', 'spreadsheet_sync', 'created_at', 'updated_at', 'created_by', 'updated_by']:
                        select_parts.append(f"p.{col}")
                    else:
                        select_parts.append(f"p.{col}") # Default to payments table

                cols_str = ", ".join(select_parts)
                query = f"SELECT p.id, {cols_str}, p.google_row_index FROM payments p LEFT JOIN orders o ON p.order_id = o.id WHERE 1=1"
                headers = custom_headers
            else:
                db_cols = ['id', 'order_id', 'merchant_id', 'payment_reference', 'amount_paid', 'payment_status', 
                           'paid_at', 'spreadsheet_sync', 'created_at', 'updated_at', 'created_by', 'updated_by']
                
                select_parts = [f"p.{col}" for col in db_cols]
                cols_str = ", ".join(select_parts)
                query = f"SELECT {cols_str}, p.google_row_index FROM payments p WHERE 1=1"
                
                # Define default headers
                headers = ['ID', 'Order ID', 'Merchant ID', 'Payment Reference', 'Amount Paid', 'Payment Status', 
                           'Paid At', 'Spreadsheet Sync', 'Created At', 'Updated At', 'Created By', 'Updated By']

            params = []

            if not sync_all:
                query += " AND (p.spreadsheet_sync = 0 OR p.spreadsheet_sync IS NULL)"
            
            if order_id:
                query += " AND p.order_id = ?"
                params.append(order_id)
            
            if merchant_id:
                query += " AND o.merchant_id = ?"
                params.append(merchant_id)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Ensure 'Payments' sheet exists
            ok, msg = self.ensure_sheet('Payments', headers, service_json, sheet_id)
            if not ok:
                 conn.close()
                 return False, msg, 0

            if not rows:
                conn.close()
                return True, "Payments sheet checked. No new payments to sync.", 0
            
            # Fetch existing data for duplicate check ONLY if needed
            needs_sheet_map = False
            for row in rows:
                g_index = row[-1]
                if not g_index:
                    needs_sheet_map = True
                    break
            
            id_to_row = {}
            id_col_idx = -1
            
            if needs_sheet_map:
                id_to_row, id_col_idx = self.get_sheet_id_map('Payments', service_json, sheet_id)

            synced_count = 0
            for row in rows:
                payment_id = row[0]
                g_index = row[-1]
                
                if custom_headers:
                    # row is (id, cols..., google_row_index)
                    row_data = [val if val is not None else '' for val in row[1:-1]]
                else:
                    # row is (cols..., google_row_index)
                    row_data = [val if val is not None else '' for val in row[:-1]]

                ok, msg, new_row_num = self.update_or_append_data('Payments', [row_data], payment_id, id_col_idx, id_to_row, service_json, sheet_id, google_row_index=g_index)
                
                if ok:
                    updates = ["spreadsheet_sync = 1"]
                    params = []
                    if new_row_num:
                         updates.append("google_row_index = ?")
                         params.append(new_row_num)
                    
                    params.append(payment_id)
                    cursor.execute(f"UPDATE payments SET {', '.join(updates)} WHERE id = ?", params)
                    synced_count += 1
            
            conn.commit()
            conn.close()
            
            return True, f"Successfully synced {synced_count} payments", synced_count
        except Exception as e:
            return False, f"Error syncing payments: {str(e)}", 0

    def sync_unsynced_expenses(self, order_id=None, sync_all=False, service_json=None, sheet_id=None, merchant_id=None):
        """
        Syncs expenses. If sync_all is True, ignores spreadsheet_sync status.
        Returns: (success, message, synced_count)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check for custom settings
            custom_headers, custom_cols = self.get_sync_settings('expenses')
            
            if custom_headers:
                # Expenses needs joins
                select_parts = []
                for col in custom_cols:
                    if col in ['customer_name', 'customer_location', 'order_number']:
                        select_parts.append(f"o.{col}")
                    else:
                        select_parts.append(f"e.{col}")

                cols_str = ", ".join(select_parts)
                query = f"SELECT e.id, {cols_str}, e.google_row_index FROM expenses e LEFT JOIN orders o ON e.order_id = o.id WHERE 1=1"
                headers = custom_headers
            else:
                db_cols = ['id', 'order_id', 'merchant_id', 'expense_name', 'expense_amount', 'spreadsheet_sync', 
                           'created_at', 'updated_at', 'created_by', 'updated_by']
                
                select_parts = [f"e.{col}" for col in db_cols]
                cols_str = ", ".join(select_parts)
                query = f"SELECT {cols_str}, e.google_row_index FROM expenses e WHERE 1=1"
                
                # Define headers for Expenses
                headers = ['ID', 'Order ID', 'Merchant ID', 'Expense Name', 'Expense Amount', 'Spreadsheet Sync', 
                           'Created At', 'Updated At', 'Created By', 'Updated By']

            params = []
            
            if not sync_all:
                query += " AND (e.spreadsheet_sync = 0 OR e.spreadsheet_sync IS NULL)"
            
            if order_id:
                query += " AND e.order_id = ?"
                params.append(order_id)
            
            if merchant_id:
                query += " AND o.merchant_id = ?"
                params.append(merchant_id)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Ensure 'Expenses' sheet exists
            ok, msg = self.ensure_sheet('Expenses', headers, service_json, sheet_id)
            if not ok:
                 conn.close()
                 return False, msg, 0

            if not rows:
                conn.close()
                return True, "Expenses sheet checked. No new expenses to sync.", 0
            
            # Fetch existing data for duplicate check ONLY if needed
            needs_sheet_map = False
            for row in rows:
                g_index = row[-1]
                if not g_index:
                    needs_sheet_map = True
                    break
            
            id_to_row = {}
            id_col_idx = -1
            
            if needs_sheet_map:
                id_to_row, id_col_idx = self.get_sheet_id_map('Expenses', service_json, sheet_id)

            synced_count = 0
            for row in rows:
                expense_id = row[0]
                g_index = row[-1]
                
                if custom_headers:
                    # row is (id, cols..., google_row_index)
                    row_data = [val if val is not None else '' for val in row[1:-1]]
                else:
                    # row is (cols..., google_row_index)
                    row_data = [val if val is not None else '' for val in row[:-1]]
                
                ok, msg, new_row_num = self.update_or_append_data('Expenses', [row_data], expense_id, id_col_idx, id_to_row, service_json, sheet_id, google_row_index=g_index)
                
                if ok:
                    updates = ["spreadsheet_sync = 1"]
                    params = []
                    if new_row_num:
                         updates.append("google_row_index = ?")
                         params.append(new_row_num)
                    
                    params.append(expense_id)
                    cursor.execute(f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?", params)
                    synced_count += 1
            
            conn.commit()
            conn.close()
            
            return True, f"Successfully synced {synced_count} expenses", synced_count
        except Exception as e:
            return False, f"Error syncing expenses: {str(e)}", 0

    def pull_from_sheet(self, sheet_name, table_name, service_json=None, sheet_id=None, merchant_id=None):
        """
        Generic pull logic: Fetches data from sheet and updates/inserts into DB.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. Get mapping settings
            custom_headers, custom_cols = self.get_sync_settings(table_name)
            
            # 2. Fetch data from Google Sheet
            service, spreadsheet_id = self.get_service(service_json, sheet_id)
            try:
                read_result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'"
                ).execute()
            except Exception as e:
                return False, f"Could not read sheet '{sheet_name}': {str(e)}", 0

            values = read_result.get('values', [])
            if not values or len(values) < 2:
                return True, f"Sheet '{sheet_name}' is empty or has no data rows.", 0

            sheet_headers = [h.strip().lower() for h in values[0]]
            rows = values[1:]

            # 3. Process mapping
            # We need to know which sheet column index maps to which DB column.
            mapping = {} # db_col_name -> sheet_index
            
            if custom_headers:
                for i, h in enumerate(custom_headers):
                    h_lower = h.lower()
                    if h_lower in sheet_headers:
                        mapping[custom_cols[i]] = sheet_headers.index(h_lower)
            else:
                # Fallback to default headers for the table
                # This part would need explicit defaults if custom settings are missing.
                # For simplicity, if no custom settings, we use the header names as DB col names (loosely)
                for i, h in enumerate(sheet_headers):
                    col_name = h.replace(' ', '_').lower()
                    mapping[col_name] = i

            # ID column is special
            id_col_in_sheet = -1
            if 'id' in mapping:
                id_col_in_sheet = mapping['id']
            elif 'id' in sheet_headers:
                id_col_in_sheet = sheet_headers.index('id')

            updated_count = 0
            inserted_count = 0

            for row in rows:
                if not any(row): continue # Skip empty rows
                
                # Extract values for this row
                record_data = {}
                for db_col, sheet_idx in mapping.items():
                    if sheet_idx < len(row):
                        record_data[db_col] = row[sheet_idx]
                    else:
                        record_data[db_col] = None

                # Resolve ID
                record_id = record_data.get('id') if id_col_in_sheet >= 0 else None
                
                # Handle joined/calculated fields (ignore them for DB updates)
                # Some fields in custom_cols might be from joins like o.customer_name
                # We should only update fields that exist in the target table.
                
                # Get target table columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_cols = [c[1] for c in cursor.fetchall()]
                
                # Filter record_data to only include columns that exist in the table
                db_record = {k: v for k, v in record_data.items() if k in table_cols}
                
                # Special Logic for foreign keys
                # If order_number is provided but order_id is missing/invalid, try to resolve it
                if 'order_number' in record_data and ('order_id' not in db_record or not db_record['order_id']):
                    cursor.execute("SELECT id FROM orders WHERE order_number = ?", (record_data['order_number'],))
                    res = cursor.fetchone()
                    if res and 'order_id' in table_cols:
                        db_record['order_id'] = res['id']

                # Mark as synced so we don't push it back immediately
                db_record['spreadsheet_sync'] = 1
                
                # INJECT MERCHANT ID
                if merchant_id and 'merchant_id' in table_cols and not db_record.get('merchant_id'):
                    db_record['merchant_id'] = merchant_id

                if record_id and str(record_id).strip():
                    # CHECK IF EXISTS
                    cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (record_id,))
                    if cursor.fetchone():
                        # UPDATE
                        # Build SET clause
                        # Remove ID from set
                        if 'id' in db_record: del db_record['id']
                        
                        cols = db_record.keys()
                        set_clause = ", ".join([f"{c} = ?" for c in cols])
                        vals = list(db_record.values())
                        vals.append(record_id)
                        
                        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", vals)
                        updated_count += 1
                        continue
                else:
                    # NATURAL KEY DETECTION (Prevent duplicates for rows without IDs)
                    match_id = None
                    if table_name == 'orders' and db_record.get('order_number'):
                        cursor.execute("SELECT id FROM orders WHERE order_number = ?", (db_record['order_number'],))
                        res = cursor.fetchone()
                        if res: match_id = res['id']
                    elif table_name == 'order_items' and db_record.get('order_id') and db_record.get('item_name'):
                        # Order Items: order_id, item_name, created_at
                        if db_record.get('created_at'):
                            cursor.execute("SELECT id FROM order_items WHERE order_id = ? AND item_name = ? AND created_at = ?", 
                                         (db_record['order_id'], db_record['item_name'], db_record['created_at']))
                        else:
                            cursor.execute("SELECT id FROM order_items WHERE order_id = ? AND item_name = ?", 
                                         (db_record['order_id'], db_record['item_name']))
                        res = cursor.fetchone()
                        if res: match_id = res['id']
                    elif table_name == 'payments' and db_record.get('order_id') and db_record.get('amount_paid'):
                        # Payments: order_id, amount_paid
                        cursor.execute("SELECT id FROM payments WHERE order_id = ? AND amount_paid = ?",
                                     (db_record['order_id'], db_record['amount_paid']))
                        res = cursor.fetchone()
                        if res: match_id = res['id']
                    elif table_name == 'expenses' and db_record.get('order_id') and db_record.get('expense_name'):
                        # Expenses: order_id, expense_name, expense_amount
                        cursor.execute("SELECT id FROM expenses WHERE order_id = ? AND expense_name = ? AND expense_amount = ?",
                                     (db_record['order_id'], db_record['expense_name'], db_record.get('expense_amount')))
                        res = cursor.fetchone()
                        if res: match_id = res['id']
                    
                    if match_id:
                        # UPDATE instead of INSERT
                        if 'id' in db_record: del db_record['id']
                        cols = db_record.keys()
                        set_clause = ", ".join([f"{c} = ?" for c in cols])
                        vals = list(db_record.values())
                        vals.append(match_id)
                        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", vals)
                        updated_count += 1
                        continue

                # INSERT if not matched by ID or ID is empty
                # We should probably avoid inserting if critical fields like 'name' or 'order_id' are missing
                if table_name == 'order_items' and not db_record.get('order_id'):
                    continue # Can't add item without order
                
                if db_record:
                    # Remove ID if it's empty to let DB autoincrement
                    if 'id' in db_record and (not db_record['id'] or not str(db_record['id']).strip()):
                        del db_record['id']
                        
                    cols = db_record.keys()
                    placeholders = ", ".join(["?" for _ in cols])
                    cursor.execute(f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})", list(db_record.values()))
                    inserted_count += 1

            conn.commit()
            conn.close()
            
            total = updated_count + inserted_count
            return True, f"Pulled {total} records from '{sheet_name}' ({updated_count} updated, {inserted_count} new).", total

        except Exception as e:
            return False, f"Error pulling from '{sheet_name}': {str(e)}", 0

    def pull_all_merchant_data(self, entities, service_json=None, sheet_id=None, merchant_id=None):
        """
        Pull multiples entities for a merchant.
        """
        results = {}
        success = True
        
        # Mapping of entity name to (sheet_name, table_name)
        entity_map = {
            'orders': ('Orders', 'orders'),
            'order_items': ('OrderItems', 'order_items'),
            'payments': ('Payments', 'payments'),
            'expenses': ('Expenses', 'expenses')
        }
        
        # Define priority order (Orders first for FK resolution)
        entity_order = ['orders', 'order_items', 'payments', 'expenses']
        
        # Sort entities based on priority
        sorted_entities = sorted([e for e in entities if e in entity_map], 
                                key=lambda e: entity_order.index(e) if e in entity_order else 99)

        for entity in sorted_entities:
            sheet, table = entity_map[entity]
            ok, msg, count = self.pull_from_sheet(sheet, table, service_json, sheet_id, merchant_id=merchant_id)
            results[entity] = f"{count} pulled" if ok else f"Failed: {msg}"
            if not ok: success = False
                
        return success, results
