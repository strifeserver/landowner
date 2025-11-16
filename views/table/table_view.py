import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from views.table.table_filters import create_filter_window, apply_advanced_filters
from views.table.treeview_styles import apply_treeview_style
from views.table.table_buttons import on_add, on_edit, on_delete


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

        self.current_page = 1
        self.items_per_page = 10

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

        self.create_search_and_filter(table_container)
        self.create_treeview_table(table_container)
        self.render_rows()

    def create_treeview_table(self, parent):
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.X, expand=False)

        table_container = tk.Frame(tree_frame)
        table_container.pack(fill=tk.X, expand=True)

        self.vsb = ttk.Scrollbar(table_container, orient="vertical")
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_container,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            height=8,
            style="Custom.Treeview",
            yscrollcommand=self.vsb.set,
            xscrollcommand=lambda *args: self.hsb.set(*args),
        )
        self.tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.vsb.config(command=self.tree.yview)

        self.hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.hsb.pack(fill=tk.X)

        # Pagination Controls (moved here)
        nav_frame = tk.Frame(tree_frame)
        nav_frame.pack(fill=tk.X, pady=(5, 10))

        self.prev_btn = tk.Button(
            nav_frame, text="Previous", command=self.load_previous_page
        )
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.page_label = tk.Label(nav_frame, text=f"Page {self.current_page}")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(nav_frame, text="Next", command=self.load_next_page)
        self.next_btn.pack(side=tk.LEFT)

        #Loop Columns
        for col, label in zip(self.columns, self.column_labels):
            self.tree.heading(col, text=label)
            if col.lower() == "id":
                self.tree.column(col, width=50, anchor="center", stretch=False)
            elif col.lower() == "customid":
                self.tree.column(col, width=100, anchor="center", stretch=False)
            else:
                self.tree.column(col, width=150, anchor="w", stretch=True)
        #Loop Columns

        self.tree.tag_configure("oddrow", background="#f5f5f5")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_header(self, title):
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(5, 2))
        tk.Label(title_frame, text=title, font=("Arial", 12, "bold")).pack(
            side=tk.LEFT, padx=10
        )

        tk.Button(title_frame, text="Add", command=lambda: on_add(self), width=10).pack(
            side=tk.RIGHT, padx=10
        )
        self.edit_btn = tk.Button(
            title_frame,
            text="Edit",
            state=tk.DISABLED,
            command=lambda: on_edit(self),
            width=10,
        )
        self.edit_btn.pack(side=tk.RIGHT, padx=10)
        self.delete_btn = tk.Button(
            title_frame,
            text="Delete",
            state=tk.DISABLED,
            command=lambda: on_delete(self),
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
        tk.Button(search_frame, text="Refresh", command=self.refresh_table, width=10).pack(side=tk.LEFT, padx=10)

    def create_pagination_controls(self, parent):
        nav_frame = tk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(5, 10))

        self.prev_btn = tk.Button(
            nav_frame, text="Previous", command=self.load_previous_page
        )
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.page_label = tk.Label(nav_frame, text=f"Page {self.current_page}")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(nav_frame, text="Next", command=self.load_next_page)
        self.next_btn.pack(side=tk.LEFT)

    def configure_styles(self):
        apply_treeview_style()

    def render_rows(self):
        if self.controller_callback:
            self.filtered_data = self.controller_callback(
                searchAll=self.search_entry.get().strip().lower(),
                page=self.current_page,
            )

        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(self.filtered_data):
            values = [row.get(col, "") for col in self.columns]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, iid=str(idx), values=values, tags=(tag,))

        self.edit_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)

        showing = len(self.filtered_data)
        total = getattr(self, "total_rows", showing)
        total_pages = getattr(self, "total_pages", 1)

        self.page_label.config(
            text=f"Page {self.current_page} / {total_pages}   (Showing {showing} of {total} rows)"
        )

        # Enable/disable navigation buttons
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)


    def load_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_rows()

    def load_next_page(self):
        self.current_page += 1
        self.render_rows()

    def on_add(self):
        self.trigger_controller_method("create")

    def on_edit(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        row = self.filtered_data[index]
        row_id = row.get("id")
        self.trigger_controller_method("edit", id=row_id)

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
            self.trigger_controller_method("destroy", id=row_id)
            self.render_rows()

    def on_search(self, event=None):
        self.current_page = 1
        self.render_rows()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        self.edit_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        self.delete_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def filter_all(self):
        create_filter_window(self)
        
    def refresh_table(self):
        print('Refresh Table')
        self.current_page = 1     # optional, reset pagination
        self.search_entry.delete(0, tk.END)  # optional, clear search
        self.render_rows()
        
        

    def apply_advanced_filters(self):
        apply_advanced_filters(self)

    def trigger_controller_method(self, method_name, id=None, data=None):
        if not hasattr(self, "controller_class"):
            print("Controller class not set.")
            return
        method = getattr(self.controller_class, method_name, None)
        if not callable(method):
            print(f"Method '{method_name}' not found in controller.")
            return
        try:
            if method_name == "create":
                return method()
            elif method_name == "store":
                return method(data)
            elif method_name == "edit":
                return method(id)
            elif method_name == "update":
                return method(id, data)
            elif method_name == "destroy":
                return method(id)
            else:
                print(f"Unsupported method '{method_name}'")
        except TypeError as e:
            print(f"Error calling '{method_name}': {e}")
