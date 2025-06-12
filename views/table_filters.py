import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta, date


def create_filter_window(self):
    # Avoid multiple open windows
    if hasattr(self, 'filter_window') and self.filter_window.winfo_exists():
        self.filter_window.lift()
        return

    self.filter_window = tk.Toplevel(self)
    self.filter_window.title("Advanced Filters")
    self.filter_window.geometry("300x650")
    self.filter_window.transient(self)
    self.filter_window.protocol("WM_DELETE_WINDOW", lambda: self.filter_window.destroy())

    tk.Label(self.filter_window, text="Enter filter values below:").pack(pady=5)
    self.filter_entries = {}

    for col in self.columns:
        if col in ["created_at", "updated_at"]:
            continue
        label_text = self.column_labels[self.columns.index(col)] if self.column_labels else col
        row_frame = tk.Frame(self.filter_window)
        row_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(row_frame, text=f"{label_text}:", width=12, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(row_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entries[col] = entry

    # Only load/setup date filters if enabled
    if getattr(self, 'enable_date_filters', True):
        setup_date_filters(self, self.filter_window)

    tk.Button(self.filter_window, text="Apply Filters", command=self.apply_advanced_filters).pack(pady=10)


def setup_date_filters(self, window):
    def bind_default_date(entry):
        def on_focus(event):
            if not entry.get():
                entry.set_date(date.today())
        entry.bind("<FocusIn>", on_focus)

    def setup_toggle(variable, entry):
        def toggle_state(*_):
            state = "normal" if variable.get() else "disabled"
            entry.config(state=state)
            if state == "disabled":
                entry.delete(0, tk.END)
        variable.trace_add("write", toggle_state)
        toggle_state()

    # Date Created
    self.date_created_enabled = tk.BooleanVar(value=False)
    dc_frame = tk.Frame(window)
    dc_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Checkbutton(dc_frame, text="Date Created", variable=self.date_created_enabled).pack(side=tk.LEFT)
    self.date_created_entry = DateEntry(dc_frame, date_pattern="yyyy-mm-dd", width=16)
    self.date_created_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.date_created_entry)
    setup_toggle(self.date_created_enabled, self.date_created_entry)

    # Date Updated
    self.date_updated_enabled = tk.BooleanVar(value=False)
    du_frame = tk.Frame(window)
    du_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Checkbutton(du_frame, text="Date Updated", variable=self.date_updated_enabled).pack(side=tk.LEFT)
    self.date_updated_entry = DateEntry(du_frame, date_pattern="yyyy-mm-dd", width=16)
    self.date_updated_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.date_updated_entry)
    setup_toggle(self.date_updated_enabled, self.date_updated_entry)

    # Date Created Range
    self.enable_range_var = tk.BooleanVar(value=False)
    tk.Checkbutton(window, text="Enable Date Created Range", variable=self.enable_range_var).pack(pady=5)

    # From
    from_frame = tk.Frame(window)
    from_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(from_frame, text="Date Created From:", width=14, anchor="w").pack(side=tk.LEFT)
    self.created_at_from = DateEntry(from_frame, date_pattern="yyyy-mm-dd", width=16)
    self.created_at_from.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.created_at_from)

    # To
    to_frame = tk.Frame(window)
    to_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(to_frame, text="Date Created To:", width=14, anchor="w").pack(side=tk.LEFT)
    self.created_at_to = DateEntry(to_frame, date_pattern="yyyy-mm-dd", width=16)
    self.created_at_to.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.created_at_to)

    def toggle_range_state(*_):
        state = "normal" if self.enable_range_var.get() else "disabled"
        for entry in [self.created_at_from, self.created_at_to]:
            entry.config(state=state)
            if state == "disabled":
                entry.delete(0, tk.END)

    self.enable_range_var.trace_add("write", toggle_range_state)
    toggle_range_state()


def apply_advanced_filters(self):
    filters = {}

    for col, entry in self.filter_entries.items():
        val = entry.get().strip()
        if val:
            filters[col] = val.lower()

    # Helper to parse date and optionally add a day
    def parse_date_plus(date_str, plus_days=True):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if plus_days:
                date_obj += timedelta(days=1)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    # Only apply date logic if enabled
    if getattr(self, 'enable_date_filters', True):
        if self.date_created_enabled.get():
            d = self.date_created_entry.get().strip()
            if d:
                filters["created_at_from"] = d
                filters["created_at_to"] = parse_date_plus(d)

        if self.date_updated_enabled.get():
            d = self.date_updated_entry.get().strip()
            if d:
                filters["updated_at_from"] = d
                filters["updated_at_to"] = parse_date_plus(d)

        if self.enable_range_var.get():
            d_from = self.created_at_from.get().strip()
            d_to = self.created_at_to.get().strip()
            if d_from:
                filters["created_at_from"] = d_from
            if d_to:
                filters["created_at_to"] = parse_date_plus(d_to)

    if self.controller_callback:
        self.filtered_data = self.controller_callback(filters=filters)
    else:
        self.filtered_data = [
            row
            for row in self.original_data
            if all(
                str(row.get(col, "")).lower().find(val) != -1
                for col, val in filters.items()
                if col not in {
                    "created_at_from", "created_at_to",
                    "updated_at_from", "updated_at_to"
                }
            )
        ]

    self.render_rows()
