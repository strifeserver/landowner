# views/sheet_sync/sheet_sync_settings_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import os
from models.db_config import DB_PATH

class SheetSyncSettingsView(tk.Toplevel):
    def __init__(self, parent, table_name, callback=None):
        super().__init__(parent)
        self.table_name = table_name
        self.callback = callback
        self.title(f"Configure Sheet Sync: {table_name.title()}")
        self.geometry("500x600")
        
        # Load existing settings
        saved_settings = self._load_settings()
        
        # Get all available columns (including new ones)
        available_cols = self._get_available_columns()
        
        # Merge
        self.current_settings = self._merge_settings(saved_settings, available_cols)
            
        self._setup_ui()
        
    def _load_settings(self):
        try:
            from models.sheet_sync_settings import SheetSyncSettings
            record = SheetSyncSettings.find_by_table(self.table_name)
            if record and record[2]: # settings_json is index 2
                return json.loads(record[2])
        except Exception as e:
            print(f"Error loading sync settings: {e}")
        return []

    def _get_available_columns(self):
        """Fetch columns from DB"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Base columns
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            cols = [col[1] for col in cursor.fetchall()]
            
            # Add joined columns for specific tables
            if self.table_name in ['payments', 'expenses', 'order_items']:
                # These are the joined fields we want available
                if self.table_name == 'order_items':
                     # order_items already has order_number, but maybe user wants customer info
                     joined_cols = ['customer_name', 'customer_location']
                else:
                     joined_cols = ['customer_name', 'customer_location', 'order_number']
                
                if self.table_name == 'order_items':
                    joined_cols.extend(['downpayment', 'remaining_balance'])

                cols.extend(joined_cols)
                
            conn.close()
            return cols
        except Exception as e:
            print(f"Error discovering columns: {e}")
            return []

    def _merge_settings(self, saved_settings, available_cols):
        if not saved_settings:
            # Create default settings
            return [{"name": col, "sync": True, "order": i} for i, col in enumerate(available_cols)]
        
        # Map existing settings by name
        saved_map = {item['name']: item for item in saved_settings}
        
        merged = []
        # 1. Add existing settings (preserving order and sync status)
        # Verify they still exist in available_cols? Optional, but good practice. 
        # For now, let's keep them to avoid deleting user config if a col is temporarily missing? 
        # Or better: Iterate available_cols to enforce schema?
        # User wants to see NEW columns.
        
        # Let's start with saved settings
        current_max_order = 0
        for item in saved_settings:
            merged.append(item)
            if item.get('order', 0) > current_max_order:
                current_max_order = item.get('order', 0)
                
        # 2. Add new available columns that are NOT in saved settings
        for col in available_cols:
            if col not in saved_map:
                current_max_order += 1
                merged.append({
                    "name": col,
                    "sync": True, # Default to sync new columns? Or False? User asked for them, likely True.
                    "order": current_max_order
                })
                
        return merged

    def _setup_ui(self):
        # Instruction
        tk.Label(self, text="Select columns to sync to Google Sheets", font=("Segoe UI", 10, "bold"), pady=10).pack()
        
        # Columns List Frame
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Scrollable list
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0")
        header_frame.pack(fill="x", pady=2)
        tk.Label(header_frame, text="Column Name", width=25, anchor="w", bg="#e0e0e0").pack(side="left", padx=5)
        tk.Label(header_frame, text="To Sync", width=10, bg="#e0e0e0").pack(side="left", padx=5)
        tk.Label(header_frame, text="Order", width=10, bg="#e0e0e0").pack(side="left", padx=5)
        
        # Rows
        self.rows = []
        # Sort by order before displaying
        self.current_settings.sort(key=lambda x: x.get('order', 999))
        
        for idx, col_data in enumerate(self.current_settings):
            self._add_row(col_data, idx)
            
        # Action Buttons
        btn_frame = tk.Frame(self, pady=20)
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="Save Settings", command=self.save, 
                  bg="#4caf50", fg="white", font=("Segoe UI", 9, "bold"), padx=20).pack()

    def _add_row(self, col_data, idx):
        row_frame = tk.Frame(self.scrollable_frame, pady=2)
        row_frame.pack(fill="x")
        
        # Name (Read-only)
        tk.Label(row_frame, text=col_data['name'], width=25, anchor="w").pack(side="left", padx=5)
        
        # To Sync Checkbox
        var = tk.BooleanVar(value=col_data.get('sync', True))
        tk.Checkbutton(row_frame, variable=var).pack(side="left", padx=25)
        
        # Order Buttons
        order_frame = tk.Frame(row_frame)
        order_frame.pack(side="left", padx=5)
        
        tk.Button(order_frame, text="↑", command=lambda: self.move_row(idx, -1), width=2).pack(side="left")
        tk.Button(order_frame, text="↓", command=lambda: self.move_row(idx, 1), width=2).pack(side="left")
        
        self.rows.append({
            "name": col_data['name'],
            "var": var,
            "frame": row_frame
        })

    def move_row(self, index, direction):
        if index + direction < 0 or index + direction >= len(self.current_settings):
            return
            
        # Swap in data
        self.current_settings[index], self.current_settings[index + direction] = \
            self.current_settings[index + direction], self.current_settings[index]
            
        # Re-render
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Header (re-add)
        header_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0")
        header_frame.pack(fill="x", pady=2)
        tk.Label(header_frame, text="Column Name", width=25, anchor="w", bg="#e0e0e0").pack(side="left", padx=5)
        tk.Label(header_frame, text="To Sync", width=10, bg="#e0e0e0").pack(side="left", padx=5)
        tk.Label(header_frame, text="Order", width=10, bg="#e0e0e0").pack(side="left", padx=5)

        self.rows = []
        for i, col_data in enumerate(self.current_settings):
            col_data['order'] = i # Update order index
            self._add_row(col_data, i)

    def save(self):
        # Update settings from vars
        final_settings = []
        for i, row in enumerate(self.rows):
            final_settings.append({
                "name": row['name'],
                "sync": row['var'].get(),
                "order": i
            })
            
        # Save to DB
        try:
            from models.sheet_sync_settings import SheetSyncSettings
            import sqlite3
            
            # Check if exists
            existing = SheetSyncSettings.find_by_table(self.table_name)
            
            if existing: # array tuple
                SheetSyncSettings.update(existing[0], settings_json=json.dumps(final_settings)) # existing[0] is ID
            else:
                SheetSyncSettings.store(
                    table_name=self.table_name,
                    settings_json=json.dumps(final_settings)
                )
                
            messagebox.showinfo("Success", "Sync settings saved successfully.")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
