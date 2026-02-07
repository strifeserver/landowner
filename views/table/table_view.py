import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from views.table.table_filters import create_filter_window, apply_advanced_filters
from views.table.treeview_styles import apply_treeview_style
from views.table.table_buttons import on_add, on_edit, on_delete, on_move_up, on_move_down


class TableView(tk.Frame):
    def __init__(self, parent, data, controller_callback=None, title="Table View", columns=None, column_labels=None, nav_id=None, *args, **kwargs,):
        super().__init__(parent, *args, **kwargs)
        self.controller_callback = controller_callback
        self.original_data = data.copy()
        self.filtered_data = data.copy()
        self.advance_filter = {}
        self.current_page = 1
        self.items_per_page = 10
        self.total_rows = 0
        self.total_pages = 1
        self.nav_id = nav_id # Store Navigation ID
        
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

        
        self.create_header(title)

        # --- Table Container ---
        table_container = tk.Frame(self)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.create_search_and_filter(table_container)
        self.create_treeview_table(table_container)
        self.render_rows()

    def get_permissions(self):
        """
        Returns a dict { 'add': bool, 'edit': bool, 'delete': bool }
        based on current user's Access Level and this Table's nav_id.
        """
        from utils.session import Session
        from models.access_level import AccessLevel
        
        user = Session.get_user()
        if not user:
            return {'add': False, 'edit': False, 'delete': False}
        
        # If nav_id is missing (e.g. Dashboard), assume read-only or full access?
        # Let's assume read-only for safety if matched content, or maybe True? 
        # Usually dashboard doesn't have add/edit table.
        if not self.nav_id:
             return {'add': True, 'edit': True, 'delete': True}

        try:
            # Fetch AccessLevel for the user
            # user.access_level is the FK ID
            al = AccessLevel.edit(user.access_level)
            if not al:
                return {'add': False, 'edit': False, 'delete': False}
                
            perms = {
                'add': self.nav_id in al.get_permissions_list('add'),
                'edit': self.nav_id in al.get_permissions_list('edit'),
                'delete': self.nav_id in al.get_permissions_list('delete')
            }
            return perms
        except Exception as e:
            return {'add': False, 'edit': False, 'delete': False}

    def create_treeview_table(self, parent):
        #Table style Config
        table_style_config = {
            "table_height": 10,   
            "table_heading_font_size": 12,   
            "table_row_font_size": 11,   
            "table_font": "Arial",   
            "table_row_height": 30,   
        }
        #Table style Config

        
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
            height=table_style_config['table_height'] , #Table Height
            style="Custom.Treeview",
            yscrollcommand=self.vsb.set,
            xscrollcommand=lambda *args: self.hsb.set(*args),
        )
        self.tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.vsb.config(command=self.tree.yview)
        
        self.configure_styles(table_style_config)
                
        self.hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.hsb.pack(fill=tk.X)

        # Pagination Controls (moved here)
        nav_frame = tk.Frame(tree_frame)
        nav_frame.pack(fill=tk.X, pady=(5, 10))

        self.prev_btn = tk.Button(nav_frame, text="Previous", command=self.load_previous_page)
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
            elif col.lower() == "is_locked":
                self.tree.column(col, width=120, anchor="center", stretch=False)
            elif col.lower() == "account_status":
                self.tree.column(col, width=120, anchor="center", stretch=False)
            else:
                self.tree.column(col, width=150, anchor="w", stretch=True)
        #Loop Columns

        self.tree.tag_configure("oddrow", background="#f5f5f5")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_header(self, title):
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(5, 2))
        tk.Label(title_frame, text=title, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)

        # Check Permissions
        perms = self.get_permissions()

        if perms['add']:
            tk.Button(title_frame, text="Add", command=lambda: on_add(self), width=10).pack(side=tk.RIGHT, padx=10)
        
        if perms['edit']:
            self.edit_btn = tk.Button(
                title_frame,
                text="Edit",
                state=tk.DISABLED,
                command=lambda: on_edit(self),
                width=10,
            )
            self.edit_btn.pack(side=tk.RIGHT, padx=10)
        else:
            self.edit_btn = None # Flag that it doesn't exist
        
        if perms['delete']:
            self.delete_btn = tk.Button(
                title_frame,
                text="Delete",
                state=tk.DISABLED,
                command=lambda: on_delete(self),
                width=10,
            )
            self.delete_btn.pack(side=tk.RIGHT, padx=10)
        else:
            self.delete_btn = None

        # Add Move Up/Down buttons for Navigations module only
        if title == "Navigations":
            self.move_down_btn = tk.Button(
                title_frame,
                text="Move Down",
                state=tk.DISABLED,
                command=lambda: on_move_down(self),
                width=10,
            )
            self.move_down_btn.pack(side=tk.RIGHT, padx=10)

            self.move_up_btn = tk.Button(
                title_frame,
                text="Move Up",
                state=tk.DISABLED,
                command=lambda: on_move_up(self),
                width=10,
            )
            self.move_up_btn.pack(side=tk.RIGHT, padx=10)
        else:
            self.move_up_btn = None
            self.move_down_btn = None

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

    def configure_styles(self, config):
        apply_treeview_style(config)

    def render_rows(self):
        if self.controller_callback:

            window_open = (
                hasattr(self, "filter_window")
                and self.filter_window.winfo_exists()
            )

            if window_open:
                rows = self.controller_callback(
                    filters=self.advance_filter,
                    page=self.current_page,
                )
            else:
                rows = self.controller_callback(
                    searchAll=self.search_entry.get().strip().lower(),
                    page=self.current_page,
                )

            # ✅ rows ONLY — pagination already set by controller_callback
            self.filtered_data = rows or []

        # -----------------------
        # Render table rows
        # -----------------------
        self.tree.delete(*self.tree.get_children())

        for idx, row in enumerate(self.filtered_data):
            values = [getattr(row, col, "") for col in self.columns]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=values, tags=(tag,))

        showing = len(self.filtered_data)

        self.page_label.config(
            text=f"Page {self.current_page} / {self.total_pages}   "
                f"(Showing {showing} of {self.total_rows} rows)"
        )

        self.prev_btn.config(
            state=tk.NORMAL if self.current_page > 1 else tk.DISABLED
        )
        self.next_btn.config(
            state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED
        )


    def load_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_rows()

    def load_next_page(self):
        if hasattr(self, "total_pages") and self.current_page < self.total_pages:
            self.current_page += 1
            self.render_rows()


    # def on_add(self):
    #     self.trigger_controller_method("create")

    # def on_edit(self):
    #     selected = self.tree.selection()
        
    #     if not selected:
    #         return
    #     index = int(selected[0])
    #     row = self.filtered_data[index]

        
    #     row_id = row.get("id")
    #     self.trigger_controller_method("edit", id=row_id)

    # def on_delete(self):
    #     selected = self.tree.selection()
    #     if not selected:
    #         return
    #     index = int(selected[0])
    #     row = self.filtered_data[index]
    #     row_id = row.get("id", None)
    #     if row_id is None:
    #         messagebox.showerror(
    #             "Delete Error", "No 'id' field found in the selected row."
    #         )
    #         return
    #     if messagebox.askyesno(
    #         "Confirm Delete", f"Are you sure you want to delete row with ID: {row_id}?"
    #     ):
    #         self.original_data = [
    #             r for r in self.original_data if r.get("id") != row_id
    #         ]
    #         self.filtered_data = [
    #             r for r in self.filtered_data if r.get("id") != row_id
    #         ]
    #         self.trigger_controller_method("destroy", id=row_id)
    #         self.render_rows()

    def on_search(self, event=None):
        self.current_page = 1
        self.render_rows()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if hasattr(self, 'edit_btn') and self.edit_btn:
            self.edit_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        
        if hasattr(self, 'delete_btn') and self.delete_btn:
            self.delete_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        
        # Enable/disable move buttons for Navigations
        if hasattr(self, 'move_up_btn') and self.move_up_btn:
            self.move_up_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        
        if hasattr(self, 'move_down_btn') and self.move_down_btn:
            self.move_down_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def filter_all(self):
        create_filter_window(self)
        
    def refresh_table(self):
        self.current_page = 1     # optional, reset pagination
        self.search_entry.delete(0, tk.END)  # optional, clear search
        self.render_rows()
        
        

    def apply_advanced_filters(self):
        self.advance_filter = apply_advanced_filters(self)
        self.current_page = 1
        
        if not self.controller_callback:
            self._apply_local_filters()
                    
        self.render_rows()

    def _apply_local_filters(self):
        """Helper to filter data locally when no controller is available."""
        self.filtered_data = []
        for row in self.original_data:
            match = True
            for col, val in self.advance_filter.items():
                if col in ["created_at_from", "created_at_to", "updated_at_from", "updated_at_to"]:
                    continue
                
                # Robustly get value whether row is a dict or object
                row_val = getattr(row, col, "") if not isinstance(row, dict) else row.get(col, "")
                if str(row_val).lower().find(str(val)) == -1:
                    match = False
                    break
            
            # Additional date range logic if needed could go here
            if match:
                self.filtered_data.append(row)

    def trigger_controller_method(self, method_name, id=None, data=None):
        if not hasattr(self, "controller_class"):
            return

        method = getattr(self.controller_class, method_name, None)
        if not callable(method):
            return

        try:
            if method_name == "create":
                return method()
            elif method_name == "store":
                return method(data)
            elif method_name == "edit":
                return method(data)
            elif method_name == "update":
                return method(id, data)
            elif method_name == "destroy":
                return method(id)
            elif method_name == "move_up":
                return method(id)
            elif method_name == "move_down":
                return method(id)
            else:
                pass
        except TypeError as e:
            pass
