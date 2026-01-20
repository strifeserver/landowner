import tkinter as tk
from tkinter import ttk, messagebox
from models.navigation import Navigation
from models.access_level import AccessLevel
from controllers.AccessLevelController import AccessLevelController

class AccessLevelPermissionsView:
    def __init__(self, parent_master, access_level_id):
        """
        parent_master: The parent Tk widget (e.g. Toplevel or Frame)
        access_level_id: The ID of the access level to edit
        """
        self.root = tk.Toplevel(parent_master)
        self.root.title("Manage Permissions")
        self.root.geometry("1000x600")
        
        self.access_level_id = access_level_id
        self.controller = AccessLevelController()
        
        # Load Data
        self.access_level = AccessLevel.edit(self.access_level_id)
        if not self.access_level:
            messagebox.showerror("Error", "Access Level not found!")
            self.root.destroy()
            return

        self.navigations = Navigation.index()
        
        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, pady=10)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=f"Permissions for: {self.access_level.access_level_name}", 
                 font=("Arial", 14, "bold")).pack()

        # Content Frame
        content_frame = tk.Frame(self.root, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)

        # Scrollable Canvas for Matrix
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Draw the Matrix
        self.draw_matrix()

        # Footer (Save Button)
        footer_frame = tk.Frame(self.root, pady=10)
        footer_frame.pack(fill="x")
        tk.Button(footer_frame, text="Save Permissions", command=self.save, 
                  bg="green", fg="white", font=("Arial", 12)).pack()

    def draw_matrix(self):
        # Headers
        headers = ["Navigation Menu", "View", "Add", "Edit", "Delete", "Export", "Import"]
        for col, text in enumerate(headers):
            lbl = tk.Label(self.scrollable_frame, text=text, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=15)
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        # Pre-load permissions into sets for easy lookup
        # Each is a set of navigation_ids (int)
        self.perms = {
            "view": set(self.access_level.get_permissions_list("view")),
            "add": set(self.access_level.get_permissions_list("add")),
            "edit": set(self.access_level.get_permissions_list("edit")),
            "delete": set(self.access_level.get_permissions_list("delete")),
            "export": set(self.access_level.get_permissions_list("export")),
            "import": set(self.access_level.get_permissions_list("import")),
        }

        # Store IntVar variables to retrieve values later
        # Structure: self.vars[nav_id][perm_type] = IntVar
        self.vars = {}

        for row_idx, nav in enumerate(self.navigations, start=1):
            nav_id = nav.id
            self.vars[nav_id] = {}
            
            # Navigation Name
            tk.Label(self.scrollable_frame, text=nav.menu_name, anchor="w", padx=5, borderwidth=1, relief="solid").grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            
            # Checkboxes
            perm_types = ["view", "add", "edit", "delete", "export", "import"]
            for col_idx, p_type in enumerate(perm_types, start=1):
                var = tk.IntVar()
                if nav_id in self.perms[p_type]:
                    var.set(1)
                
                self.vars[nav_id][p_type] = var
                
                cb = tk.Checkbutton(self.scrollable_frame, variable=var)
                cb.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)

    def save(self):
        # Reconstruct the CSV strings
        new_perms = {
            "view": [],
            "add": [],
            "edit": [],
            "delete": [],
            "export": [],
            "import": [],
        }

        for nav_id, p_vars in self.vars.items():
            for p_type, var in p_vars.items():
                if var.get() == 1:
                    new_perms[p_type].append(nav_id)

        # Update the Access Level object using the helper
        for p_type, id_list in new_perms.items():
            self.access_level.set_permissions_list(p_type, id_list)

        # Prepare data for update
        update_data = {
            "access_level_name": self.access_level.access_level_name,
            "access_level_code": self.access_level.access_level_code,
            "view": self.access_level.view,
            "add": getattr(self.access_level, "add"), # add is a python keyword, use getattr to be safe or self.access_level.add if valid
            "edit": self.access_level.edit,
            "delete": self.access_level.delete,
            "export": self.access_level.export,
            "import": getattr(self.access_level, "import"),
        }
        
        # Handle 'add' and 'import' specifically if they clash? 
        # Actually in python 'import' is a keyword, 'add' is not (set.add is, but not bare word).
        # We need to access the attributes via getattr/dict because 'import' is a keyword.
        update_data["add"] = getattr(self.access_level, "add")
        update_data["import"] = getattr(self.access_level, "import")

        try:
            # We need to manually call update on the service or controller
            # The current AccessLevelController.update takes (id, data)
            self.controller.update(self.access_level_id, update_data)
            messagebox.showinfo("Success", "Permissions saved successfully!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            print(e)
