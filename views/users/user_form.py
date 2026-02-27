import tkinter as tk
from tkinter import ttk
from utils.alert import Alert
from models.user import User
from models.access_level import AccessLevel

class UserForm(tk.Toplevel):
    def __init__(self, parent_master, item_id=None, callback=None, initial_data=None, **kwargs):
        """
        parent_master: The parent Tk widget
        item_id: User ID to edit, or None for Add mode
        callback: Function to call after successful save
        initial_data: Data passed from controller
        """
        super().__init__(parent_master)
        self.callback = callback or kwargs.get("on_save_callback")
        self.initial_data = initial_data or kwargs
        
        # Robustly get user_id from arguments or initial_data
        self.user_id = item_id
        if not self.user_id and self.initial_data:
            if isinstance(self.initial_data, dict):
                self.user_id = self.initial_data.get("id")
            else:
                self.user_id = getattr(self.initial_data, "id", None)

        mode_text = "Edit" if self.user_id else "Add"
        self.title(f"{mode_text} User")
        self.geometry("450x650")
        self.resizable(False, False)
        self.config(bg="#f8f9fa")

        # Data Loading
        self.user_data = None
        if self.user_id:
            # If initial_data is the object itself, use it. Otherwise, fetch from DB.
            if self.initial_data and (isinstance(self.initial_data, User) or (isinstance(self.initial_data, dict) and "username" in self.initial_data)):
                 self.user_data = self.initial_data
            else:
                 self.user_data = User.edit(self.user_id)
                 
            if not self.user_data:
                Alert.error("User not found!")
                self.destroy()
                return

        self.setup_ui()

    def setup_ui(self):
        container = tk.Frame(self, bg="#f8f9fa", padx=30, pady=30)
        container.pack(fill="both", expand=True)

        # 1. Employee ID (ONLY in EDIT mode, READONLY)
        if self.user_id:
            tk.Label(container, text="Employee ID:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
            self.id_entry = tk.Entry(container, font=("Arial", 10), state="normal")
            self.id_entry.insert(0, self.user_data.customId or self.initial_data.get("customId", ""))
            self.id_entry.config(state="readonly")
            self.id_entry.pack(fill="x", pady=(0, 15))

        # 2. Username
        tk.Label(container, text="Username:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
        self.username_entry = tk.Entry(container, font=("Arial", 10))
        self.username_entry.pack(fill="x", pady=(0, 15))
        if self.user_data:
            self.username_entry.insert(0, self.user_data.username or "")

        # 3. Email
        tk.Label(container, text="Email:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
        self.email_entry = tk.Entry(container, font=("Arial", 10))
        self.email_entry.pack(fill="x", pady=(0, 15))
        if self.user_data:
            self.email_entry.insert(0, self.user_data.email or "")

        # 4. Password (ONLY in CREATE mode)
        if not self.user_id:
            tk.Label(container, text="Password:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
            self.password_entry = tk.Entry(container, show="*", font=("Arial", 10))
            self.password_entry.pack(fill="x", pady=(0, 15))

        # 5. Account Status (Dropdown)
        tk.Label(container, text="Account Status:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
        self.status_var = tk.StringVar(value="Active")
        self.status_combo = ttk.Combobox(container, textvariable=self.status_var, state="readonly")
        self.status_combo['values'] = ("Active", "Inactive", "Pending")
        self.status_combo.pack(fill="x", pady=(0, 15))
        if self.user_data:
            current_status = (self.user_data.account_status or "active").capitalize()
            self.status_var.set(current_status)

        # 6. Access Level (Dropdown)
        tk.Label(container, text="Access Level:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
        self.access_levels = AccessLevel.index()
        self.access_level_map = {al.access_level_name: al.id for al in self.access_levels}
        
        self.access_level_var = tk.StringVar()
        self.access_level_combo = ttk.Combobox(container, textvariable=self.access_level_var, state="readonly")
        self.access_level_combo['values'] = list(self.access_level_map.keys())
        self.access_level_combo.pack(fill="x", pady=(0, 15))
        
        if self.user_data:
            # Find the name for the current ID
            current_name = next((al.access_level_name for al in self.access_levels if al.id == self.user_data.access_level), "")
            self.access_level_var.set(current_name)
        elif self.access_level_map:
            # Default to first if found
            self.access_level_var.set(list(self.access_level_map.keys())[0])

        # 7. Is Locked (Checkbox)
        self.is_locked_var = tk.IntVar(value=0)
        self.lock_check = tk.Checkbutton(
            container, 
            text="Is Locked", 
            variable=self.is_locked_var, 
            bg="#f8f9fa", 
            font=("Arial", 10)
        )
        self.lock_check.pack(anchor="w", pady=(0, 15))
        if self.user_data:
            self.is_locked_var.set(1 if self.user_data.is_locked else 0)

        # 8. Spreadsheet Validation (Checkbox)
        self.spreadsheet_validation_var = tk.IntVar(value=0)
        self.spreadsheet_check = tk.Checkbutton(
            container, 
            text="Spreadsheet Validation", 
            variable=self.spreadsheet_validation_var, 
            bg="#f8f9fa", 
            font=("Arial", 10)
        )
        self.spreadsheet_check.pack(anchor="w", pady=(0, 15))
        if self.user_data:
            self.spreadsheet_validation_var.set(1 if getattr(self.user_data, 'spreadsheet_validation', 0) else 0)

        # 9. Last Login (Read-only, ONLY in EDIT mode)
        if self.user_id and self.user_data:
            tk.Label(container, text="Last Login:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w")
            last_login_value = getattr(self.user_data, 'last_login', 'Never') or 'Never'
            self.last_login_entry = tk.Entry(container, font=("Arial", 10), state="normal")
            self.last_login_entry.insert(0, last_login_value)
            self.last_login_entry.config(state="readonly")
            self.last_login_entry.pack(fill="x", pady=(0, 5))
            
            # Reset Login Button (8 days ago)
            reset_btn = tk.Button(
                container, 
                text="Reset Login", 
                command=self.reset_login_8_days,
                bg="#6c757d",
                fg="white",
                font=("Arial", 8),
                padx=5,
                pady=2
            )
            reset_btn.pack(anchor="w", pady=(0, 15))

        # 10. Actions
        btn_frame = tk.Frame(container, bg="#f8f9fa")
        btn_frame.pack(fill="x", side="bottom")

        save_btn = tk.Button(
            btn_frame, 
            text="Save User", 
            bg="#28a745", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=self.save,
            pady=8
        )
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = tk.Button(
            btn_frame, 
            text="Cancel", 
            command=self.destroy,
            pady=8
        )
        cancel_btn.pack(side="right")

    def reset_login_8_days(self):
        """Sets the user's last login to 8 days ago for testing."""
        from datetime import datetime, timedelta
        
        eight_days_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Update in DB directly for immediate effect
            User.update(self.user_id, last_login=eight_days_ago)
            
            # Update UI
            self.last_login_entry.config(state="normal")
            self.last_login_entry.delete(0, "end")
            self.last_login_entry.insert(0, eight_days_ago)
            self.last_login_entry.config(state="readonly")
            
            Alert.success(f"Last login reset to {eight_days_ago} (8 days ago).", "Reset Successful")
        except Exception as e:
            Alert.error(f"Failed to reset login: {str(e)}")

    def save(self):
        # 1. Show loading alert
        loading_popup = Alert.loading("Saving user data...", "Processing")
        self.update() # Force UI update

        # 2. Harvest Data
        data = {
            "username": self.username_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "account_status": self.status_var.get().lower(),
            "access_level": self.access_level_map.get(self.access_level_var.get()),
            "is_locked": self.is_locked_var.get(),
            "spreadsheet_validation": self.spreadsheet_validation_var.get()
        }

        # For ADD mode, include Employee ID and Password
        if not self.user_id:
            custom_id = self.initial_data.get("customId")
            if not custom_id:
                try:
                    custom_id = User.get_next_custom_id()
                except Exception as e:

                    custom_id = "000001"
            
            data["customId"] = custom_id
            data["password"] = self.password_entry.get()

        # 3. Communicate with Controller (via callback passed from table_buttons)
        if self.callback:
            try:
                response = self.callback(data)
                
                # Close loading
                if loading_popup:
                    loading_popup.destroy()
                
                if isinstance(response, dict) and response.get("success"):
                    Alert.success(response.get("message", "Operation successful"))
                    self.destroy()
                elif isinstance(response, dict) and not response.get("success"):
                    Alert.error(response.get("message", "Operation failed"), title="Error")
            except Exception as e:
                if loading_popup:
                    loading_popup.destroy()
                Alert.error(f"Unexpected error: {str(e)}")
        else:
            if loading_popup:
                loading_popup.destroy()
            self.destroy() # Fallback
