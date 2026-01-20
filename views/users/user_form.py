import tkinter as tk
from tkinter import ttk
from utils.Alert import Alert
from models.user import User
from models.access_level import AccessLevel

class UserForm(tk.Toplevel):
    def __init__(self, parent_master, item_id=None, callback=None, **kwargs):
        """
        parent_master: The parent Tk widget
        item_id: User ID to edit, or None for Add mode
        callback: Function to call after successful save (returns controller response)
        """
        super().__init__(parent_master)
        self.user_id = item_id
        self.callback = callback
        
        # Initial Data passed from controller (like customId)
        self.initial_data = kwargs
        
        mode_text = "Edit" if self.user_id else "Add"
        self.title(f"{mode_text} User")
        self.geometry("450x550")
        self.resizable(False, False)
        self.config(bg="#f8f9fa")

        # Data Loading
        self.user_data = None
        if self.user_id:
            # Use User object if passed directly in kwargs (optional)
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
        self.lock_check.pack(anchor="w", pady=(0, 20))
        if self.user_data:
            self.is_locked_var.set(1 if self.user_data.is_locked else 0)

        # 7. Actions
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

    def save(self):
        # 1. Harvest Data
        data = {
            "username": self.username_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "account_status": self.status_var.get().lower(),
            "access_level": self.access_level_map.get(self.access_level_var.get()),
            "is_locked": self.is_locked_var.get()
        }

        # For ADD mode, include Employee ID and Password
        if not self.user_id:
            data["customId"] = self.initial_data.get("customId")
            data["password"] = self.password_entry.get()

        # 2. Communicate with Controller (via callback passed from table_buttons)
        if self.callback:
            response = self.callback(data)
            
            if isinstance(response, dict) and response.get("success"):
                self.destroy()
        else:
            self.destroy() # Fallback
