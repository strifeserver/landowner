# views/crud_builder/crud_builder_form.py
import tkinter as tk
from tkinter import ttk
import json
from utils.Alert import Alert
from views.crud_builder.dropdown_options_form import DropdownOptionsForm

class CrudBuilderForm(tk.Toplevel):
    def __init__(self, parent, callback=None, initial_data=None, **kwargs):
        super().__init__(parent)
        self.title("CRUD Builder - Configuration")
        self.geometry("900x700")
        self.callback = callback
        self.initial_data = initial_data
        
        self.fields_rows = []
        
        self._setup_ui()
        
        if initial_data:
            self._load_data(initial_data)
        else:
            # Add some default fields
            self.add_field_row("Name", "name", "text", True, True)

    def _setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header Section
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Maintenance Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(header_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=10, sticky="w")
        
        # Sorting Section
        sort_frame = tk.Frame(main_frame)
        sort_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(sort_frame, text="Default Sort Field:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.sort_field_var = tk.StringVar(value="id")
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_field_var, values=["id", "created_at"])
        self.sort_combo.grid(row=0, column=1, padx=10, sticky="w")
        
        tk.Label(sort_frame, text="Direction:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=(20, 0), sticky="w")
        self.sort_dir_var = tk.StringVar(value="ASC")
        self.sort_dir_combo = ttk.Combobox(sort_frame, textvariable=self.sort_dir_var, values=["ASC", "DESC"], width=10)
        self.sort_dir_combo.grid(row=0, column=3, padx=10, sticky="w")

        # Fields Section
        fields_header = tk.Frame(main_frame)
        fields_header.pack(fill="x")
        tk.Label(fields_header, text="Field Definitions", font=("Arial", 12, "bold")).pack(side="left")
        tk.Button(fields_header, text="+ Add Field", command=self.add_field_row).pack(side="right")
        
        # Scrollable Area for Fields
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Table Headers for Fields
        headers = ["Alias (Display Name)", "Field Name (DB)", "Type", "Ops", "Visible", "Editable", "Actions"]
        for col, text in enumerate(headers):
            tk.Label(self.scrollable_frame, text=text, font=("Arial", 9, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Bottom Buttons
        btn_frame = tk.Frame(self, pady=20)
        btn_frame.pack(fill="x", side="bottom")
        
        tk.Button(btn_frame, text="Generate Module", command=self.submit, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20, height=2).pack()

    def add_field_row(self, alias="", name="", ftype="text", visible=True, editable=True, options=None):
        row_idx = len(self.fields_rows) + 1
        
        alias_var = tk.StringVar(value=alias)
        name_var = tk.StringVar(value=name)
        type_var = tk.StringVar(value=ftype)
        visible_var = tk.BooleanVar(value=visible)
        editable_var = tk.BooleanVar(value=editable)
        options_data = options or []
        
        # Link alias to name auto-generation
        def on_alias_change(*args, nv=name_var, av=alias_var):
            if not self.initial_data: # Only auto-gen for new fields
                nv.set(av.get().lower().replace(" ", "_"))
        
        alias_var.trace_add("write", on_alias_change)
        
        alias_entry = tk.Entry(self.scrollable_frame, textvariable=alias_var, width=25)
        name_entry = tk.Entry(self.scrollable_frame, textvariable=name_var, width=25)
        type_combo = ttk.Combobox(self.scrollable_frame, textvariable=type_var, values=["text", "number", "date", "dropdown"], width=10)
        visible_chk = tk.Checkbutton(self.scrollable_frame, variable=visible_var)
        editable_chk = tk.Checkbutton(self.scrollable_frame, variable=editable_var)
        
        # Options button (initially hidden/disabled unless dropdown)
        options_btn = tk.Button(self.scrollable_frame, text="Options", state="disabled", command=lambda: self.manage_options(row_idx))
        
        delete_btn = tk.Button(self.scrollable_frame, text="Delete", command=lambda r=row_idx: self.delete_row(r))
        
        alias_entry.grid(row=row_idx, column=0, padx=5, pady=2)
        name_entry.grid(row=row_idx, column=1, padx=5, pady=2)
        type_combo.grid(row=row_idx, column=2, padx=5, pady=2)
        visible_chk.grid(row=row_idx, column=4, padx=5, pady=2)
        editable_chk.grid(row=row_idx, column=5, padx=5, pady=2)
        options_btn.grid(row=row_idx, column=3, padx=5, pady=2)
        delete_btn.grid(row=row_idx, column=6, padx=5, pady=2)
        
        # Update options button state based on type
        def on_type_change(*args, tv=type_var, ob=options_btn):
            if tv.get() == "dropdown":
                ob.config(state="normal", bg="#e1f5fe")
            else:
                ob.config(state="disabled", bg="#f0f0f0")
        
        type_var.trace_add("write", on_type_change)
        on_type_change() # Init
        
        self.fields_rows.append({
            "idx": row_idx,
            "alias_var": alias_var,
            "name_var": name_var,
            "type_var": type_var,
            "visible_var": visible_var,
            "editable_var": editable_var,
            "options_data": options_data,
            "widgets": [alias_entry, name_entry, type_combo, options_btn, visible_chk, editable_chk, delete_btn]
        })
        
        # Update sort options
        self._update_sort_options()

    def delete_row(self, idx):
        for row in self.fields_rows:
            if row["idx"] == idx:
                for w in row["widgets"]:
                    w.destroy()
                self.fields_rows.remove(row)
                break
        self._update_sort_options()

    def manage_options(self, idx):
        for row in self.fields_rows:
            if row["idx"] == idx:
                def save_callback(opts, r=row):
                    r["options_data"] = opts
                
                DropdownOptionsForm(self, initial_options=row["options_data"], callback=save_callback)
                break

    def _update_sort_options(self):
        options = ["id", "created_at"]
        for row in self.fields_rows:
            fname = row["name_var"].get()
            if fname and fname not in options:
                options.append(fname)
        self.sort_combo["values"] = options

    def _load_data(self, data):
        self.name_entry.insert(0, data.get("name", ""))
        self.sort_field_var.set(data.get("sort_field", "id"))
        self.sort_dir_var.set(data.get("sort_direction", "ASC"))
        
        fields_json = data.get("fields_json")
        if fields_json:
            fields = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
            for f in fields:
                self.add_field_row(
                    f.get("alias"), 
                    f.get("name"), 
                    f.get("type"), 
                    f.get("visible"), 
                    f.get("editable"),
                    f.get("options")
                )

    def submit(self):
        name = self.name_entry.get().strip()
        if not name:
            Alert.error("Please enter a maintenance name.")
            return
            
        fields = []
        for row in self.fields_rows:
            fname = row["name_var"].get().strip()
            alias = row["alias_var"].get().strip()
            if not fname or not alias:
                continue
            fields.append({
                "alias": alias,
                "name": fname,
                "type": row["type_var"].get(),
                "visible": row["visible_var"].get(),
                "editable": row["editable_var"].get(),
                "options": row["options_data"] if row["type_var"].get() == "dropdown" else []
            })
            
        if not fields:
            Alert.error("Please add at least one field.")
            return
            
        data = {
            "name": name,
            "fields_json": json.dumps(fields),
            "sort_field": self.sort_field_var.get(),
            "sort_direction": self.sort_dir_var.get()
        }
        
        if self.callback:
            response = self.callback(data)
            if response.get("success"):
                self.destroy()
            else:
                Alert.error(response.get("message", "Operation failed."))
        else:
            self.destroy()
