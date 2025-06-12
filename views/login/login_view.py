# views/login_view.py
import tkinter as tk
from tkinter import messagebox
from views.main_window import MainWindow  # Add this import
class LoginView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("300x200")

        tk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.handle_login).pack(pady=20)

        self.root.mainloop()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.controller.login(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.root.destroy()
            MainWindow()
            # Call your next view (e.g. Main Dashboard)
        else:
            messagebox.showerror("Error", "Invalid credentials.")
