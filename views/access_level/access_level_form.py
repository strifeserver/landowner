import tkinter as tk
from tkinter import ttk
from utils.Alert import Alert
from models.navigation import Navigation
from models.access_level import AccessLevel

class AccessLevelForm(tk.Toplevel):
    def __init__(self, parent_master, item_id=None, callback=None):
        """
        parent_master: The parent Tk widget
        item_id: ID to edit, or None for Add mode
        callback: Function to call after successful save (optional)
        """
        super().__init__(parent_master)
        self.access_level_id = item_id
        self.callback = callback
        
        # Lazy import to avoid circular dependency
        from controllers.AccessLevelController import AccessLevelController
        self.controller = AccessLevelController()
        
        mode_text = "Edit" if self.access_level_id else "Add"
        self.title(f"{mode_text} Access Level")
        self.geometry("1100x700")
        
        # Data Loading
        self.navigations = Navigation.index()
        
        if self.access_level_id:
            self.access_level = AccessLevel.edit(self.access_level_id)
            if not self.access_level:
                messagebox.showerror("Error", "Access Level not found!")
                self.destroy()
                return
        else:
            # Create a dummy object for 'Add' mode with empty defaults
            self.access_level = AccessLevel() 

        self.setup_ui()

    def setup_ui(self):
        # 1. Top Section: Inputs
        top_frame = tk.Frame(self, pady=20, padx=20, bg="#f0f0f0")
        top_frame.pack(fill="x")
        
        # Grid layout for inputs
        tk.Label(top_frame, text="Access Level Name:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = tk.Entry(top_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5)
        if self.access_level.access_level_name:
            self.name_entry.insert(0, self.access_level.access_level_name)

        tk.Label(top_frame, text="Access Level Code:", bg="#f0f0f0", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        self.code_entry = tk.Entry(top_frame, width=20)
        self.code_entry.grid(row=0, column=3, padx=5)
        if self.access_level.access_level_code:
            self.code_entry.insert(0, self.access_level.access_level_code)

        # 2. Middle Section: Permission Matrix (Scrollable)
        matrix_container = tk.Frame(self, padx=10, pady=10)
        matrix_container.pack(fill="both", expand=True)

        tk.Label(matrix_container, text="Permissions Matrix", font=("Arial", 12, "bold", "underline")).pack(anchor="w", pady=(0, 10))

        # Scrollable Canvas
        canvas = tk.Canvas(matrix_container)
        scrollbar = ttk.Scrollbar(matrix_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.draw_matrix()

        # 3. Footer: Save Button
        footer_frame = tk.Frame(self, pady=15, bg="#e0e0e0")
        footer_frame.pack(fill="x")
        
        tk.Button(footer_frame, text="Cancel", command=self.destroy, width=15).pack(side="right", padx=20)
        tk.Button(footer_frame, text="Save Access Level", command=self.save, 
                  bg="green", fg="white", font=("Arial", 11, "bold"), width=20).pack(side="right")

    def draw_matrix(self):
        # Headers
        headers = ["Navigation Menu"] + ["View", "Add", "Edit", "Delete", "Export", "Import"]
        for col, text in enumerate(headers):
            bg = "#dddddd" if col == 0 else "#eeeeee"
            lbl = tk.Label(self.scrollable_frame, text=text, font=("Arial", 9, "bold"), 
                           borderwidth=1, relief="solid", width=15, bg=bg)
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        # Helper method safely gets permissions whether we are in Add or Edit mode
        def get_perm_set(perm_type):
            return set(self.access_level.get_permissions_list(perm_type))

        self.perms = {
            "view": get_perm_set("view"),
            "add": get_perm_set("add"),
            "edit": get_perm_set("edit"),
            "delete": get_perm_set("delete"),
            "export": get_perm_set("export"),
            "import": get_perm_set("import"),
        }

        self.vars = {}

        for row_idx, nav in enumerate(self.navigations, start=1):
            nav_id = nav.id
            self.vars[nav_id] = {}
            
            # Row Color Alternation
            bg = "white" if row_idx % 2 != 0 else "#f9f9f9"

            # Check logic for 'Add' Mode (default checks?) -> Currently default unchecked.
            
            # Navigation Name
            tk.Label(self.scrollable_frame, text=nav.menu_name, anchor="w", padx=10, 
                     borderwidth=1, relief="solid", bg=bg).grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            
            # Checkboxes
            perm_types = ["view", "add", "edit", "delete", "export", "import"]
            for col_idx, p_type in enumerate(perm_types, start=1):
                var = tk.IntVar()
                if nav_id in self.perms[p_type]:
                    var.set(1)
                
                self.vars[nav_id][p_type] = var
                
                cb = tk.Checkbutton(self.scrollable_frame, variable=var, bg=bg, activebackground=bg)
                cb.grid(row=row_idx, column=col_idx, sticky="ns", padx=1, pady=1)

    def save(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        
        if not name or not code:
            Alert.warning("Name and Code are required.", title="Validation")
            return

        # 1. Harvest Permissions
        new_perms = {ptype: [] for ptype in ["view", "add", "edit", "delete", "export", "import"]}
        for nav_id, p_vars in self.vars.items():
            for p_type, var in p_vars.items():
                if var.get() == 1:
                    new_perms[p_type].append(nav_id)

        # 2. Update Local Object (Helper method updates attributes)
        self.access_level.access_level_name = name
        self.access_level.access_level_code = code
        
        for p_type, id_list in new_perms.items():
            self.access_level.set_permissions_list(p_type, id_list)

        # 3. Prepare Data for Controller
        data = {
            "access_level_name": self.access_level.access_level_name,
            "access_level_code": self.access_level.access_level_code,
            "view": self.access_level.view,
            "add": getattr(self.access_level, "add"),
            "edit": self.access_level.edit,
            "delete": self.access_level.delete,
            "export": self.access_level.export,
            "import": getattr(self.access_level, "import"),
        }

        # 4. Delegate to callback (table_buttons standardized on_submit)
        if self.callback:
            response = self.callback(data)
            if isinstance(response, dict) and response.get("success"):
                self.destroy()
        else:
            self.destroy()
