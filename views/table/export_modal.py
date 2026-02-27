import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from utils.alert import Alert

class ExportModal(tk.Toplevel):
    def __init__(self, parent, table_view_instance):
        super().__init__(parent)
        self.table_view = table_view_instance
        self.title("Export Order Data")
        self.geometry("400x350")
        self.resizable(False, False)
        self.grab_set()
        
        # State
        self.include_payments = tk.BooleanVar(value=True)
        self.include_expenses = tk.BooleanVar(value=True)
        
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self, padx=25, pady=25)
        main_frame.pack(fill="both", expand=True)

        tk.Label(
            main_frame, 
            text="Export Configuration", 
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 20))

        # Info Box
        info_box = tk.Frame(main_frame, bg="#e3f2fd", padx=10, pady=10)
        info_box.pack(fill="x", pady=(0, 20))
        tk.Label(
            info_box, 
            text="Orders and Order Items are automatically included.",
            bg="#e3f2fd",
            wraplength=320,
            justify="left",
            font=("Arial", 9, "italic")
        ).pack()

        # Checkboxes
        tk.Checkbutton(
            main_frame, 
            text="Include Payments History", 
            variable=self.include_payments,
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)

        tk.Checkbutton(
            main_frame, 
            text="Include Expenses History", 
            variable=self.include_expenses,
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)

        # Selection Count
        selected_ids = self.get_selected_ids()
        count_text = f"Selected Orders for Export: {len(selected_ids)}" if selected_ids else "Exporting Current View (All rows in table)"
        
        tk.Label(
            main_frame,
            text=count_text,
            fg="#1565c0",
            font=("Arial", 10, "bold")
        ).pack(pady=20)

        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(side="bottom", fill="x")

        tk.Button(
            btn_frame, 
            text="Export to JSON", 
            command=self.run_export,
            bg="#2e7d32",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2
        ).pack(fill="x")

    def get_selected_ids(self):
        """Returns list of IDs for selected rows in treeview."""
        selected_items = self.table_view.tree.selection()
        ids = []
        for item in selected_items:
            values = self.table_view.tree.item(item, 'values')
            if values:
                # Find ID column index
                try:
                    id_idx = self.table_view.columns.index('id')
                    ids.append(values[id_idx])
                except:
                    pass
        return ids

    def run_export(self):
        selected_ids = self.get_selected_ids()
        
        # If nothing selected, export all currently filtered data
        if not selected_ids:
            selected_ids = []
            for row in self.table_view.filtered_data:
                rid = getattr(row, 'id', None)
                if rid is None and isinstance(row, dict):
                    rid = row.get('id')
                if rid is not None:
                    selected_ids.append(rid)

        if not selected_ids:
            Alert.error("No data available to export.")
            return

        # Choose File Location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if not file_path:
            return

        try:
            # Resolve IDs to integers if possible for better DB performance
            processed_ids = []
            for oid in selected_ids:
                try: processed_ids.append(int(oid))
                except: processed_ids.append(oid)
            
            from controllers.OrdersController import OrdersController
            export_data = OrdersController.get_export_data(processed_ids)
            
            # Filter keys based on checkboxes
            for entry in export_data:
                if not self.include_payments.get():
                    entry["payments"] = []
                if not self.include_expenses.get():
                    entry["expenses"] = []

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, default=str)

            Alert.success(f"Successfully exported {len(export_data)} orders to JSON.")
            self.destroy()
            
        except Exception as e:
            Alert.error(f"Export failed: {str(e)}")
