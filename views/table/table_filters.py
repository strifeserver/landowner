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
    self.filter_window.geometry("380x600") # Slightly wider, fixed height
    self.filter_window.transient(self)
    
    # 1. Main Container with Scrollbar
    main_frame = tk.Frame(self.filter_window)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(main_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=360)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 2. Field Container (inside scrollable_frame)
    tk.Label(scrollable_frame, text="Apply advanced search criteria:", font=("Segoe UI", 10, "bold")).pack(pady=10)
    
    self.filter_entries = {}

    # Fields to exclude from advanced filter
    exclude_fields = ["id", "created_at", "updated_at", "deleted_at", "deleted_by", "password"]

    for col in self.columns:
        if col.lower() in exclude_fields:
            continue
        label_text = (
            self.column_labels[self.columns.index(col)] if self.column_labels else col
        )
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(row_frame, text=f"{label_text}:", width=14, anchor="w").pack(
            side=tk.LEFT
        )
        entry = tk.Entry(row_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entries[col] = entry

    # Setup date filters inside the same scrollable area
    setup_date_filters(self, scrollable_frame)

    # 3. Action Buttons (Fixed at bottom, outside scroll area)
    btn_frame = tk.Frame(self.filter_window, pady=10, relief="raised", bd=1)
    btn_frame.pack(fill=tk.X, side="bottom")

    # Inner container to ensure logical centering
    inner_btn_frame = tk.Frame(btn_frame)
    inner_btn_frame.pack()

    def clear_and_reset():
        for entry in self.filter_entries.values():
            entry.delete(0, tk.END)
        if hasattr(self, 'enable_date_filters'):
            self.enable_date_filters.set(False)
        self.apply_advanced_filters()
        self.filter_window.destroy()

    tk.Button(
        inner_btn_frame, text="Apply Filters", command=self.apply_advanced_filters, width=15, 
        bg="#7066e0", fg="white", font=("Segoe UI", 9, "bold")
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        inner_btn_frame, text="Clear", command=clear_and_reset, width=10
    ).pack(side=tk.LEFT, padx=5)


def _parse_date_plus(date_str, plus_days=True):
    """Utility to handle date range math for SQL-like queries."""
    try:
        from datetime import datetime, timedelta
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if plus_days:
            date_obj += timedelta(days=1)
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, ImportError):
        return date_str


def apply_advanced_filters(self):
    filters = {}

    for col, entry in self.filter_entries.items():
        val = entry.get().strip()
        if val:
            filters[col] = val.lower()

    if hasattr(self, 'enable_date_filters') and self.enable_date_filters.get():
        if self.date_created_enabled.get():
            d = self.date_created_entry.get().strip()
            if d:
                filters["created_at_from"] = d
                filters["created_at_to"] = _parse_date_plus(d)

        if self.date_updated_enabled.get():
            d = self.date_updated_entry.get().strip()
            if d:
                filters["updated_at_from"] = d
                filters["updated_at_to"] = _parse_date_plus(d)

        if self.enable_range_var.get():
            d_from = self.created_at_from.get().strip()
            d_to = self.created_at_to.get().strip()
            if d_from:
                filters["created_at_from"] = d_from
            if d_to:
                filters["created_at_to"] = _parse_date_plus(d_to)

    return filters
