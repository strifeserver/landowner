import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry

class TableView(tk.Frame):
    def __init__(self, parent, columns, data, controller_callback=None, title="Table View", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.columns = columns
        self.controller_callback = controller_callback
        self.original_data = data
        self.filtered_data = data
        

        # Title Bar
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(5, 2))
        tk.Label(title_frame, text=title, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)

        add_btn = tk.Button(title_frame, text="Add", command=self.on_add, width=10)
        add_btn.pack(side=tk.RIGHT, padx=10)

        self.edit_btn = tk.Button(title_frame, text="Edit", state=tk.DISABLED, command=self.on_edit, width=10)
        self.edit_btn.pack(side=tk.RIGHT, padx=10)

        self.delete_btn = tk.Button(title_frame, text="Delete", state=tk.DISABLED, command=self.on_delete, width=10)
        self.delete_btn.pack(side=tk.RIGHT, padx=10)

        # Container
        table_container = tk.Frame(self)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Single Search Input
        search_frame = tk.Frame(table_container)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(search_frame, text="Search(all):").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        self.filter_all = tk.Button(search_frame, text="More Filters", command=self.filter_all, width=10)
        self.filter_all.pack(side=tk.LEFT, padx=10)

        # Treeview and Scrollbar
        tree_frame = tk.Frame(table_container, height=200)
        tree_frame.pack(fill=tk.BOTH, expand=False)

        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", selectmode="browse", height=8)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Render initial rows
        self.render_rows()

    def render_rows(self):
        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(self.filtered_data):
            values = [row.get(col, '') for col in self.columns]
            self.tree.insert('', tk.END, iid=str(idx), values=values)

        # Disable buttons after refresh
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

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            index = int(selected[0])
            row = self.filtered_data[index]
            print(f"Deleting row ID: {row['id']}")
            self.render_rows()

    def on_search(self, event=None):
        keyword = self.search_entry.get().strip().lower()

        if self.controller_callback:
            self.filtered_data = self.controller_callback(searchAll=keyword)
  
        else:
            self.filtered_data = [
                row for row in self.original_data
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
        filter_window.geometry("300x400")

        tk.Label(filter_window, text="Enter filter values below:").pack(pady=5)

        self.filter_entries = {}

        # Create input fields for each column
        for col in self.columns:
            row_frame = tk.Frame(filter_window)
            row_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(row_frame, text=col + ":", width=12, anchor="w").pack(side=tk.LEFT)

            # Use DateEntry for date fields
            if col in ["created_at", "updated_at"]:
                entry = DateEntry(row_frame, date_pattern="yyyy-mm-dd", width=16)
            else:
                entry = tk.Entry(row_frame)

            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.filter_entries[col] = entry

        apply_btn = tk.Button(filter_window, text="Apply Filters", command=self.apply_advanced_filters)
        apply_btn.pack(pady=10)


    def apply_advanced_filters(self):
        filters = {col: entry.get().strip().lower() for col, entry in self.filter_entries.items() if entry.get().strip()}

        if self.controller_callback:
            self.filtered_data = self.controller_callback(filters=filters)
        else:
            self.filtered_data = [
                row for row in self.original_data
                if all(str(row.get(col, '')).lower().find(val) != -1 for col, val in filters.items())
            ]

        self.render_rows()
