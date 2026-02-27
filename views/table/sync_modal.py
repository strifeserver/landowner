import tkinter as tk
from tkinter import ttk
import threading
import time
from utils.alert import Alert

class SyncModal(tk.Toplevel):
    def __init__(self, parent, table_view):
        super().__init__(parent)
        self.title("Google Sheet Synchronization")
        self.geometry("500x400") # Increased size for new layout
        self.grab_set()
        self.resizable(False, False)
        self.table_view = table_view
        
        self.cooldown = 5 # seconds
        self.setup_ui()

    def setup_ui(self):
        self.config(bg="#f8f9fa")
        main_frame = tk.Frame(self, padx=25, pady=25, bg="#f8f9fa")
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="Google Sheet Sync", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#333").pack(pady=(0, 20))

        # Checkboxes
        check_frame = tk.LabelFrame(main_frame, text="Data to Include", padx=15, pady=15, bg="#f8f9fa", font=("Segoe UI", 9, "bold"))
        check_frame.pack(fill="x", pady=5)

        # All / Force Sync Checkbox
        self.sync_all_var = tk.IntVar(value=0)
        tk.Checkbutton(check_frame, text="All (Force Sync)", variable=self.sync_all_var, 
                       command=self.toggle_all, bg="#f8f9fa", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5)

        self.sync_entities = {
            'orders': tk.IntVar(value=1),
            'order_items': tk.IntVar(value=1),
            'payments': tk.IntVar(value=0),
            'expenses': tk.IntVar(value=0)
        }
        
        # Link orders -> order_items
        def on_orders_change(*args):
            if self.sync_entities['orders'].get() == 1:
                 self.sync_entities['order_items'].set(1)
            # Optional: if uncheck orders, uncheck items? 
            # User didn't explicitly ask, but it makes sense.
            # else:
            #      self.sync_entities['order_items'].set(0)
                 
        self.sync_entities['orders'].trace_add("write", on_orders_change)

        # Frame for individual entities
        entities_frame = tk.Frame(check_frame, bg="#f8f9fa")
        entities_frame.pack(fill="x", padx=20)

        for i, (entity_key, var) in enumerate(self.sync_entities.items()):
            text = entity_key.replace('_', ' ').title()
            row = i // 2
            col = i % 2
            tk.Checkbutton(entities_frame, text=text, variable=var, bg="#f8f9fa", font=("Segoe UI", 10)).grid(row=row, column=col, sticky="w", padx=10, pady=5)

        # Buttons and Notes
        actions_frame = tk.Frame(main_frame, bg="#f8f9fa", pady=20)
        actions_frame.pack(fill="x")
        
        # Configure Columns Button
        tk.Button(actions_frame, text="Configure Columns", command=self.open_column_config,
                  bg="#e0e0e0", font=("Segoe UI", 9)).pack(pady=(0, 15))

        # Push Section
        push_container = tk.Frame(actions_frame, bg="#f8f9fa")
        push_container.pack(side="left", expand=True)
        
        self.push_btn = tk.Button(push_container, text="Push Data", command=self.handle_push, 
                                  bg="#e3f2fd", width=15, font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        self.push_btn.pack()
        tk.Label(push_container, text="Upload local data\nto Google Sheets", font=("Segoe UI", 8), fg="#666", bg="#f8f9fa", pady=5).pack()

        # Pull Section
        pull_container = tk.Frame(actions_frame, bg="#f8f9fa")
        pull_container.pack(side="left", expand=True)

        self.pull_btn = tk.Button(pull_container, text="Pull Data", command=self.handle_pull, 
                                  bg="#f1f8e9", width=15, font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2")
        self.pull_btn.pack()
        tk.Label(pull_container, text="Download cloud data\nto local database", font=("Segoe UI", 8), fg="#666", bg="#f8f9fa", pady=5).pack()

        self.status_label = tk.Label(main_frame, text="", fg="#d32f2f", font=("Segoe UI", 9, "italic"), bg="#f8f9fa")
        self.status_label.pack(pady=10)

    def toggle_all(self):
        state = self.sync_all_var.get()
        for var in self.sync_entities.values():
            var.set(state)

    def start_cooldown(self):
        self.push_btn.config(state="disabled")
        self.pull_btn.config(state="disabled")
        
        def count_down(seconds):
            for i in range(seconds, 0, -1):
                if not self.winfo_exists(): return
                self.status_label.config(text=f"Anti-spam active. Ready in {i}s")
                time.sleep(1)
            
            if self.winfo_exists():
                self.push_btn.config(state="normal")
                self.pull_btn.config(state="normal")
                self.status_label.config(text="")

        threading.Thread(target=count_down, args=(self.cooldown,), daemon=True).start()

    def run_sync_task(self, task_type):
        selected = [k for k, v in self.sync_entities.items() if v.get() == 1]
        sync_all = self.sync_all_var.get() == 1
        
        if not selected and not sync_all:
            Alert.warning("Please select at least one entity to synchronize.", title="No Selection")
            return
            
        # If sync_all is True, force all entities to be selected if not already?
        # The user said "if All is checked then orders is checked..."
        # My toggle_all handles the visual check.
        # But if user checks All, then unchecks Orders, what happens?
        # User requirement: "All checked -> disregards spreadsheet sync".
        # So I will pass the sync_all flag.
        
        if sync_all and not selected:
             # Should practically not happen due to toggle_all, unless user manually unchecks.
             pass

        # Show loading
        loading_popup = Alert.loading(message=f"Syncing {', '.join(selected)}...", title="Cloud Sync")
        
        from utils.thread_manager import ThreadManager
        if not hasattr(self, 'thread_manager'):
            self.thread_manager = ThreadManager(self)

        def execute():
            from controllers.CloudSyncController import CloudSyncController
            if task_type == 'push':
                return CloudSyncController.push(selected, sync_all=sync_all)
            else:
                return CloudSyncController.pull(selected)
                
        def on_complete(result):
            self.finish_task(result, task_type, loading_popup)
            
        def on_error(e):
            self.finish_task({"success": False, "message": str(e)}, task_type, loading_popup)

        self.thread_manager.run_in_thread(execute, on_complete, on_error)

    def finish_task(self, result, task_type, loading_popup):
        # Ensure UI updates happen on the main thread
        def update_ui():
            try:
                # 1. Close loading popup safely
                if loading_popup and loading_popup.winfo_exists():
                    loading_popup.destroy()
                
                # 2. Show result
                if result.get("success"):
                    if task_type == 'push':
                        msg = "Data successfully pushed to Google Sheets:\n"
                        msg += "\n".join([f"• {k}: {v}" for k, v in result.get("results", {}).items()])
                        Alert.success(msg, title="Push Success")
                    else:
                        Alert.success("Data successfully pulled from Google Sheets. Your local database has been updated.", title="Pull Success")
                        self.table_view.refresh_table()
                    self.start_cooldown()
                else:
                    Alert.error(result.get("message"), title="Sync Failed")
            except Exception as e:
                pass
                # print(f"Error updating sync UI: {e}")

        self.after(0, update_ui)

    def handle_push(self):
        self.run_sync_task('push')

    def handle_pull(self):
        self.run_sync_task('pull')
        
    def open_column_config(self):
        # We need to open config for specific entities.
        # But this modal handles multiple (orders, payments, expenses).
        # Maybe show a popup to choose which one? 
        # Or just show a tabbed window?
        # For simplicity, let's just ask which one, or default to 'orders' if it's the main context?
        # The modal doesn't know the "main" context except it was likely opened from Orders view.
        # But we want to configure payments/expenses too.
        
        # Let's create a simple selection dialog or just open ALL 3 in tabs?
        # A simple Toplevel with 3 buttons is easiest.
        
        selector = tk.Toplevel(self)
        selector.title("Select Table to Configure")
        selector.geometry("300x250")
        
        tk.Label(selector, text="Configure Sync Columns for:", font=("Segoe UI", 10, "bold"), pady=15).pack()
        
        def open_config(table_name):
            selector.destroy()
            from views.sheet_sync.sheet_sync_settings_view import SheetSyncSettingsView
            SheetSyncSettingsView(self, table_name)
            
        tk.Button(selector, text="Orders", command=lambda: open_config('orders'), width=20, pady=5).pack(pady=5)
        tk.Button(selector, text="Order Items", command=lambda: open_config('order_items'), width=20, pady=5).pack(pady=5)
        tk.Button(selector, text="Payments", command=lambda: open_config('payments'), width=20, pady=5).pack(pady=5)
        tk.Button(selector, text="Expenses", command=lambda: open_config('expenses'), width=20, pady=5).pack(pady=5)
