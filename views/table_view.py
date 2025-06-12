import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
# from datetime import datetime
from datetime import date  # ✅ Correct import for date.today()


class TableView(tk.Frame):
    def __init__(
        self,
        parent,
        data,
        controller_callback=None,
        title="Table View",
        columns=None,
        column_labels=None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.controller_callback = controller_callback
        self.original_data = data.copy()
        self.filtered_data = data.copy()

        if columns is None:
            if (
                controller_callback
                and hasattr(controller_callback, "model")
                and hasattr(controller_callback.model, "fields")
            ):
                self.columns = controller_callback.model.fields
            elif data and isinstance(data, list):
                self.columns = list(data[0].keys()) if data else []
            else:
                self.columns = []
        else:
            self.columns = columns

        if column_labels is None:
            if (
                controller_callback
                and hasattr(controller_callback, "model")
                and hasattr(controller_callback.model, "field_aliases")
            ):
                self.column_labels = [
                    controller_callback.model.field_aliases.get(col, col)
                    for col in self.columns
                ]
            else:
                self.column_labels = self.columns
        else:
            self.column_labels = column_labels

        self.configure_styles()
        self.create_header(title)

        # --- Table Container ---
        table_container = tk.Frame(self)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # --- Search & Filter ---
        self.create_search_and_filter(table_container)

        # --- Treeview Table ---
        self.create_treeview_table(table_container)
        self.render_rows()

    def create_treeview_table(self, parent):
        # Create a container frame
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.X, expand=False)
        # Treeview + scrollbars container
        table_container = tk.Frame(tree_frame)
        table_container.pack(fill=tk.X, expand=True)

        # Create vertical scrollbar
        self.vsb = ttk.Scrollbar(table_container, orient="vertical")
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Create Treeview widget
        self.tree = ttk.Treeview(
            table_container,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            height=8,
            style="Custom.Treeview",
            yscrollcommand=self.vsb.set,  # link vertical scrollbar
            xscrollcommand=lambda *args: self.hsb.set(
                *args
            ),  # link horizontal scrollbar
        )
        self.tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Configure vertical scrollbar to control Treeview
        self.vsb.config(command=self.tree.yview)

        # Create and pack horizontal scrollbar directly under Treeview
        self.hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.hsb.pack(fill=tk.X)

        # Configure columns
        for col, label in zip(self.columns, self.column_labels):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=200, anchor="w", stretch=True)

        # Alternating row colors
        self.tree.tag_configure("oddrow", background="#f5f5f5")
        self.tree.tag_configure("evenrow", background="white")

        # Selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_header(self, title):
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(5, 2))
        tk.Label(title_frame, text=title, font=("Arial", 12, "bold")).pack(
            side=tk.LEFT, padx=10
        )

        tk.Button(title_frame, text="Add", command=self.on_add, width=10).pack(
            side=tk.RIGHT, padx=10
        )

        self.edit_btn = tk.Button(
            title_frame, text="Edit", state=tk.DISABLED, command=self.on_edit, width=10
        )
        self.edit_btn.pack(side=tk.RIGHT, padx=10)

        self.delete_btn = tk.Button(
            title_frame,
            text="Delete",
            state=tk.DISABLED,
            command=self.on_delete,
            width=10,
        )
        self.delete_btn.pack(side=tk.RIGHT, padx=10)

    def create_search_and_filter(self, parent):
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(search_frame, text="Search(all):").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        tk.Button(
            search_frame, text="More Filters", command=self.filter_all, width=10
        ).pack(side=tk.LEFT, padx=10)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            bordercolor="black",
            borderwidth=1,
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#e1e5f2")],
            foreground=[("selected", "black")],
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="black",
            foreground="white",
            font=("Arial", 10, "bold"),
            borderwidth=1,
        )
        style.layout(
            "Custom.Treeview",
            [
                (
                    "Treeview.field",
                    {
                        "sticky": "nswe",
                        "border": "1",
                        "children": [
                            (
                                "Treeview.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        ("Treeview.treearea", {"sticky": "nswe"})
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )

    def render_rows(self):
        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(self.filtered_data):
            values = [row.get(col, "") for col in self.columns]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, iid=str(idx), values=values, tags=(tag,))
        self.edit_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)

    def on_add(self):
        print("Add button clicked.")

    def on_edit(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        row = self.filtered_data[index]
        print(f"Editing row: {row}")

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        row = self.filtered_data[index]
        row_id = row.get("id", None)
        if row_id is None:
            messagebox.showerror(
                "Delete Error", "No 'id' field found in the selected row."
            )
            return
        if messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete row with ID: {row_id}?"
        ):
            self.original_data = [
                r for r in self.original_data if r.get("id") != row_id
            ]
            self.filtered_data = [
                r for r in self.filtered_data if r.get("id") != row_id
            ]
            print(f"Deleted row with ID: {row_id}")
            self.render_rows()

    def on_search(self, event=None):
        keyword = self.search_entry.get().strip().lower()
        if self.controller_callback:
            self.filtered_data = self.controller_callback(searchAll=keyword)
        else:
            self.filtered_data = [
                row
                for row in self.original_data
                if any(keyword in str(value).lower() for value in row.values())
            ]
        self.render_rows()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)


    def filter_all(self):
        filter_window = tk.Toplevel(self)
        filter_window.title("Advanced Filters")
        filter_window.geometry("300x600")
        tk.Label(filter_window, text="Enter filter values below:").pack(pady=5)

        self.filter_entries = {}
        self.date_check_vars = {}

        for col in self.columns:
            row_frame = tk.Frame(filter_window)
            row_frame.pack(fill=tk.X, padx=10, pady=5)

            label_text = (
                self.column_labels[self.columns.index(col)]
                if self.column_labels
                else col
            )

            if col in ["created_at", "updated_at"]:
                var = tk.BooleanVar(value=False)
                self.date_check_vars[col] = var

                cb = tk.Checkbutton(row_frame, text=label_text, variable=var)
                cb.pack(side=tk.LEFT)

                entry = DateEntry(
                    row_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                def toggle_entry_state(var=var, entry=entry):
                    entry.config(state="normal" if var.get() else "disabled")

                var.trace_add(
                    "write",
                    lambda *args, var=var, entry=entry: toggle_entry_state(var, entry),
                )
            else:
                tk.Label(row_frame, text=label_text + ":", width=12, anchor="w").pack(
                    side=tk.LEFT
                )
                entry = tk.Entry(row_frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.filter_entries[col] = entry

        # Checkbox to enable/disable Created At From/To range
        self.enable_range_var = tk.BooleanVar(value=False)

        range_checkbox = tk.Checkbutton(
            filter_window,
            text="Enable Created At Range",
            variable=self.enable_range_var,
        )
        range_checkbox.pack(pady=5)

        # Created At From
        from_frame = tk.Frame(filter_window)
        from_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(from_frame, text="Created At From:", width=14, anchor="w").pack(
            side=tk.LEFT
        )
        self.created_at_from = DateEntry(
            from_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
        )
        self.created_at_from.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Created At To
        to_frame = tk.Frame(filter_window)
        to_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(to_frame, text="Created At To:", width=14, anchor="w").pack(
            side=tk.LEFT
        )
        self.created_at_to = DateEntry(
            to_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
        )
        self.created_at_to.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Toggle handler for created_at range
        def toggle_created_range():
            if self.enable_range_var.get():
                self.created_at_from.config(state="normal")
                self.created_at_to.config(state="normal")
                self.created_at_from.set_date(date.today())  # ✅ Fixed
                self.created_at_to.set_date(date.today())    # ✅ Fixed
            else:
                self.created_at_from.config(state="disabled")
                self.created_at_to.config(state="disabled")
                self.created_at_from.delete(0, tk.END)
                self.created_at_to.delete(0, tk.END)

        self.enable_range_var.trace_add("write", lambda *args: toggle_created_range())

        tk.Button(
            filter_window, text="Apply Filters", command=self.apply_advanced_filters
        ).pack(pady=10)


    def apply_advanced_filters(self):
        filters = {}

        # Standard fields
        for col, entry in self.filter_entries.items():
            val = entry.get().strip()
            if col in ["created_at", "updated_at"]:
                if self.date_check_vars[col].get() and val:
                    filters[col] = val
            else:
                if val:
                    filters[col] = val.lower()

        # Conditional range filters
        if self.enable_range_var.get():
            from_val = self.created_at_from.get().strip()
            to_val = self.created_at_to.get().strip()
            if from_val:
                filters["created_at_from"] = from_val
            if to_val:
                filters["created_at_to"] = to_val

        if self.controller_callback:
            self.filtered_data = self.controller_callback(filters=filters)
        else:
            self.filtered_data = [
                row
                for row in self.original_data
                if all(
                    str(row.get(col, "")).lower().find(val) != -1
                    for col, val in filters.items()
                    if col not in ["created_at_from", "created_at_to"]
                )
            ]

        self.render_rows()