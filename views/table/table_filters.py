import tkinter as tk
from datetime import datetime, timedelta
from views.table.table_date_filters import setup_date_filters


def create_filter_window(self):
    # Avoid multiple open windows
    if hasattr(self, "filter_window") and self.filter_window.winfo_exists():
        self.filter_window.lift()
        return

    self.filter_window = tk.Toplevel(self)
    self.filter_window.title("Advanced Filters")
    self.filter_window.geometry("300x650")
    self.filter_window.transient(self)
    self.filter_window.protocol(
        "WM_DELETE_WINDOW", lambda: self.filter_window.destroy()
    )

    tk.Label(self.filter_window, text="Enter filter values below:").pack(pady=5)
    self.filter_entries = {}

    for col in self.columns:
        if col in ["created_at", "updated_at"]:
            continue
        label_text = (
            self.column_labels[self.columns.index(col)] if self.column_labels else col
        )
        row_frame = tk.Frame(self.filter_window)
        row_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(row_frame, text=f"{label_text}:", width=12, anchor="w").pack(
            side=tk.LEFT
        )
        entry = tk.Entry(row_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entries[col] = entry

    # Setup all date filters (toggle-able)
    setup_date_filters(self, self.filter_window)

    tk.Button(
        self.filter_window, text="Apply Filters", command=self.apply_advanced_filters
    ).pack(pady=10)


def apply_advanced_filters(self):
    filters = {}

    for col, entry in self.filter_entries.items():
        val = entry.get().strip()
        if val:
            filters[col] = val.lower()

    def parse_date_plus(date_str, plus_days=True):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if plus_days:
                date_obj += timedelta(days=1)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    if self.enable_date_filters.get():
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
                if col
                not in {
                    "created_at_from",
                    "created_at_to",
                    "updated_at_from",
                    "updated_at_to",
                }
            )
        ]

    self.render_rows()
