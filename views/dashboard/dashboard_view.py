import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta

class DashboardView(tk.Frame):
    def __init__(self, parent, controller_callback=None):
        super().__init__(parent, bg="#f5f7f8")
        self.callback = controller_callback
        
        # Colors (Modern Palette)
        self.colors = {
            "income": "#10b981",    # Emerald
            "expenses": "#ef4444",  # Red
            "payments": "#3b82f6",  # Blue
            "orders": "#8b5cf6",    # Violet
            "profit": "#f59e0b",    # Amber
            "pending": "#64748b",   # Slate
            "bg": "#f5f7f8",
            "card_bg": "#ffffff"
        }
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Filter Bar
        filter_frame = tk.Frame(self, bg="white", padx=20, pady=15)
        filter_frame.pack(fill="x", side="top")
        
        tk.Label(filter_frame, text="Dashboard Filter", font=("Arial", 12, "bold"), bg="white", fg="#1e293b").pack(side="left", padx=(0, 20))
        
        # Date Selectors
        date_container = tk.Frame(filter_frame, bg="white")
        date_container.pack(side="left")
        
        # Default dates (current month)
        today = datetime.now()
        first_day = today.replace(day=1)
        
        tk.Label(date_container, text="From:", bg="white", font=("Arial", 9)).pack(side="left", padx=5)
        self.from_date = DateEntry(date_container, width=12, background='darkblue', foreground='white', borderwidth=2, year=first_day.year, month=first_day.month, day=first_day.day)
        self.from_date.pack(side="left", padx=5)
        
        tk.Label(date_container, text="To:", bg="white", font=("Arial", 9)).pack(side="left", padx=5)
        self.to_date = DateEntry(date_container, width=12, background='darkblue', foreground='white', borderwidth=2, year=today.year, month=today.month, day=today.day)
        self.to_date.pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="Apply Filter", command=self.load_data, bg="#1e293b", fg="white", padx=15, pady=5, font=("Arial", 9, "bold")).pack(side="left", padx=20)

        # 2. Main Content Area (Scrollable if needed, though cards usually fit)
        self.cards_container = tk.Frame(self, bg="#f5f7f8", padx=20, pady=20)
        self.cards_container.pack(fill="both", expand=True)
        
        # Configure Grid
        for i in range(3):
            self.cards_container.grid_columnconfigure(i, weight=1, pad=20)

    def create_card(self, row, col, title, value, color, icon=None):
        card = tk.Frame(self.cards_container, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=25)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        # Color Strip at top
        strip = tk.Frame(card, bg=color, height=4)
        strip.pack(fill="x", side="top", pady=(0, 15))
        
        tk.Label(card, text=title, font=("Arial", 10, "bold"), fg="#64748b", bg="white").pack(anchor="w")
        
        val_lbl = tk.Label(card, text=value, font=("Arial", 20, "bold"), fg="#1e293b", bg="white")
        val_lbl.pack(anchor="w", pady=(5, 0))
        
        return val_lbl

    def load_data(self):
        # Clear existing cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        # Get filtered data from controller
        filters = {
            "date_from": self.from_date.get_date().strftime("%Y-%m-%d"),
            "date_to": self.to_date.get_date().strftime("%Y-%m-%d")
        }
        
        if self.callback:
            metrics = self.callback(filters)
        else:
            # Placeholder if no callback
            metrics = {
                "income": 0, "expenses": 0, "payments": 0, "orders": 0, "profit": 0, "pending": 0
            }

        # Render Cards
        # Format currency/counts
        fmt_money = lambda x: f"₱{float(x or 0):,.2f}"
        fmt_cnt = lambda x: f"{int(x or 0):,}"

        self.create_card(0, 0, "TOTAL ORDERS", fmt_cnt(metrics.get("orders")), self.colors["orders"])
        self.create_card(0, 1, "TOTAL INCOME", fmt_money(metrics.get("income")), self.colors["income"])
        self.create_card(0, 2, "TOTAL PAYMENTS", fmt_money(metrics.get("payments")), self.colors["payments"])
        
        self.create_card(1, 0, "TOTAL EXPENSES", fmt_money(metrics.get("expenses")), self.colors["expenses"])
        self.create_card(1, 1, "NET PROFIT", fmt_money(metrics.get("profit")), self.colors["profit"])
        self.create_card(1, 2, "PENDING ORDERS", fmt_cnt(metrics.get("pending")), self.colors["pending"])
