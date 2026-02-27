from views.dashboard.dashboard_view import DashboardView
from utils.session import Session
from models.Merchants import Merchants
import sqlite3
from models.db_config import DB_PATH

class DashboardsController:
    @staticmethod
    def index_view(parent):
        return DashboardView(parent, controller_callback=DashboardsController.get_metrics)

    @staticmethod
    def index(**kwargs):
        # Fallback for generic table view if called directly (though redirected in MainWindow)
        return []

    @staticmethod
    def get_metrics(filters):
        user = Session.get_user()
        if not user:
            return {}

        # 1. Get assigned merchant IDs
        user_id_str = str(user.id)
        # Fetch all merchants to find assigned ones
        all_merchants = Merchants.index()
        merchant_ids = []
        for m in all_merchants:
            if m.merchant_users:
                assigned_users = [u.strip() for u in str(m.merchant_users).split(',') if u.strip()]
                if user_id_str in assigned_users:
                    merchant_ids.append(m.id)

        if not merchant_ids:
            return {
                "income": 0, "expenses": 0, "payments": 0, "orders": 0, "profit": 0, "pending": 0
            }

        # 2. Build Query
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        
        m_ids_str = ",".join(map(str, merchant_ids))
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total Income (Sum of orders.total_amount)
        cursor.execute(f"SELECT SUM(total_amount) FROM orders WHERE merchant_id IN ({m_ids_str}) AND date(created_at) BETWEEN ? AND ?", (date_from, date_to))
        income = cursor.fetchone()[0] or 0
        
        # Total Expenses
        cursor.execute(f"SELECT SUM(expense_amount) FROM expenses WHERE merchant_id IN ({m_ids_str}) AND date(created_at) BETWEEN ? AND ?", (date_from, date_to))
        expenses = cursor.fetchone()[0] or 0
        
        # Total Payments
        cursor.execute(f"SELECT SUM(amount_paid) FROM payments WHERE merchant_id IN ({m_ids_str}) AND date(created_at) BETWEEN ? AND ?", (date_from, date_to))
        payments = cursor.fetchone()[0] or 0
        
        # Total Orders (Count)
        cursor.execute(f"SELECT COUNT(*) FROM orders WHERE merchant_id IN ({m_ids_str}) AND date(created_at) BETWEEN ? AND ?", (date_from, date_to))
        orders_count = cursor.fetchone()[0] or 0
        
        # Pending Orders
        # We'll check for 'pending' or 'partial' statuses
        cursor.execute(f"SELECT COUNT(*) FROM orders WHERE merchant_id IN ({m_ids_str}) AND (LOWER(order_status) = 'pending' OR LOWER(order_status) = 'partial') AND date(created_at) BETWEEN ? AND ?", (date_from, date_to))
        pending_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        profit = float(income) - float(expenses)
        
        return {
            "income": income,
            "expenses": expenses,
            "payments": payments,
            "orders": orders_count,
            "profit": profit,
            "pending": pending_count
        }
