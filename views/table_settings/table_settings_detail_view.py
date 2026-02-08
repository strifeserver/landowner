# views/table_settings/table_settings_detail_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import json

class TableSettingsDetailView(tk.Toplevel):
    def __init__(self, parent, item_id=None, callback=None, initial_data=None):
        super().__init__(parent)
        self.title(f"Configure Table: {initial_data.get('table_name', 'Unknown')}")
        self.geometry("600x700")
        self.item_id = item_id
        self.callback = callback
        self.initial_data = initial_data
        
        # Load existing settings
        self.settings = []
        if initial_data.get('settings_json'):
            try:
                self.settings = json.loads(initial_data['settings_json'])
            except:
                pass
        
        # If no settings, we need to discover them from the actual table
        # For now, we'll assume the user might have to "Update" once to populate
        # But better: try to get columns from the database directly
        if not self.settings:
            self._discover_columns()

        self._setup_ui()

    def _discover_columns(self):
        """Try to fetch column names from the database for this table."""
        import sqlite3
        import os
        table_name = self.initial_data.get('table_name')
        if not table_name:
            return
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "data.db")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols = cursor.fetchall()
            conn.close()
            
            self.settings = []
            for i, col in enumerate(cols):
                self.settings.append({
                    "name": col[1],
                    "alias": col[1].replace("_", " ").title(),
                    "visible": True,
                    "order": i,
                    "capitalize_first": False
                })
        except Exception as e:
            print(f"Error discovering columns for {table_name}: {e}")

    def _setup_ui(self):
        # ----------------------------------------------------------------------
        # Top Settings (Items per page, Table Height)
        # ----------------------------------------------------------------------
        top_frame = tk.Frame(self, padx=20, pady=10)
        top_frame.pack(fill="x")
        
        tk.Label(top_frame, text="Items Per Page:").grid(row=0, column=0, sticky="w")
        self.items_per_page_var = tk.StringVar(value=str(self.initial_data.get('items_per_page', 10)))
        tk.Entry(top_frame, textvariable=self.items_per_page_var, width=10).grid(row=0, column=1, sticky="w", padx=10)
        
        tk.Label(top_frame, text="Table Height (px):").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.table_height_var = tk.StringVar(value=str(self.initial_data.get('table_height', 300)))
        tk.Entry(top_frame, textvariable=self.table_height_var, width=10).grid(row=1, column=1, sticky="w", padx=10, pady=(5,0))
        
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # ----------------------------------------------------------------------
        # Columns List
        # ----------------------------------------------------------------------
        tk.Label(self, text="Configure Columns", font=("Arial", 10, "bold")).pack(pady=5)
        
        list_container = tk.Frame(self, padx=20)
        list_container.pack(fill="both", expand=True)
        
        # Canvas and Scrollbar for the list
        self.canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._render_column_list()

        # ----------------------------------------------------------------------
        # Footer
        # ----------------------------------------------------------------------
        footer = tk.Frame(self, pady=15)
        footer.pack(side="bottom", fill="x")
        
        tk.Button(footer, text="Save Changes", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), 
                  padx=20, command=self._save).pack(side="right", padx=20)
        tk.Button(footer, text="Cancel", command=self.destroy, padx=20).pack(side="right")

    def _render_column_list(self):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Re-sort settings by order
        self.settings.sort(key=lambda x: x.get('order', 99))
        
        # Header Row
        h_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        h_frame.pack(fill="x", pady=2)
        tk.Label(h_frame, text="Order", width=5, bg="#f0f0f0", font=("Arial", 8, "bold")).pack(side="left")
        tk.Label(h_frame, text="Column Name", width=15, bg="#f0f0f0", anchor="w", font=("Arial", 8, "bold")).pack(side="left")
        tk.Label(h_frame, text="Alias / Display Name", width=20, bg="#f0f0f0", anchor="w", font=("Arial", 8, "bold")).pack(side="left")
        tk.Label(h_frame, text="Show", width=5, bg="#f0f0f0", font=("Arial", 8, "bold")).pack(side="left")
        tk.Label(h_frame, text="Cap", width=5, bg="#f0f0f0", font=("Arial", 8, "bold")).pack(side="left")

        for idx, s in enumerate(self.settings):
            row = tk.Frame(self.scrollable_frame, pady=5)
            row.pack(fill="x")
            
            # Reorder buttons
            btn_up = tk.Button(row, text="▲", width=2, command=lambda i=idx: self._move_item(i, -1))
            btn_up.pack(side="left")
            btn_down = tk.Button(row, text="▼", width=2, command=lambda i=idx: self._move_item(i, 1))
            btn_down.pack(side="left")
            
            # Column Name (Read Only)
            tk.Label(row, text=s['name'], width=15, anchor="w").pack(side="left", padx=5)
            
            # Alias Entry
            alias_var = tk.StringVar(value=s.get('alias', s['name']))
            ent = tk.Entry(row, textvariable=alias_var, width=20)
            ent.pack(side="left", padx=5)
            # Link var to settings
            def update_alias(var=alias_var, s_ref=s):
                s_ref['alias'] = var.get()
            alias_var.trace_add("write", lambda *args, v=alias_var, sr=s: update_alias(v, sr))
            
            # Visible Toggle
            vis_var = tk.BooleanVar(value=s.get('visible', True))
            tk.Checkbutton(row, variable=vis_var, command=lambda v=vis_var, sr=s: self._update_toggle(sr, 'visible', v.get())).pack(side="left", padx=5)
            
            # Capitalize Toggle
            cap_var = tk.BooleanVar(value=s.get('capitalize_first', False))
            tk.Checkbutton(row, variable=cap_var, command=lambda v=cap_var, sr=s: self._update_toggle(sr, 'capitalize_first', v.get())).pack(side="left", padx=5)

    def _move_item(self, idx, direction):
        if 0 <= idx + direction < len(self.settings):
            # Swap orders
            self.settings[idx]['order'], self.settings[idx+direction]['order'] = \
                self.settings[idx+direction]['order'], self.settings[idx]['order']
            self._render_column_list()

    def _update_toggle(self, s_ref, key, val):
        s_ref[key] = val

    def _save(self):
        try:
            data = {
                "items_per_page": int(self.items_per_page_var.get()),
                "table_height": int(self.table_height_var.get()),
                "settings_json": json.dumps(self.settings)
            }
            if self.callback:
                self.callback(data)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Items Per Page and Table Height must be numbers.")
