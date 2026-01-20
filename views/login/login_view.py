# views/login_view.py
import tkinter as tk
from tkinter import messagebox
from views.main_window import MainWindow  # Make sure this import works correctly

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

        # 🔑 Bind the Enter/Return key to the login handler
        self.root.bind('<Return>', lambda event: self.handle_login())

        self.root.mainloop()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            user = self.controller.login(username, password)
            
            if user:
                from utils.session import Session
                Session.set_user(user)
                
                messagebox.showinfo("Success", f"Welcome, {user.username}!")
                self.root.destroy()
                MainWindow()  # You might want to pass the controller here if needed
                
        except ValueError as e:
             messagebox.showerror("Login Failed", str(e))
        except Exception as e:
             messagebox.showerror("Error", f"An unexpected error occurred: {e}")
