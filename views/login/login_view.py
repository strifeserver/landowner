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

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Login", command=self.handle_login).pack(side=tk.LEFT, padx=10)

        # 🔑 Check for Quick Login (active session)
        from utils.session import Session
        if Session.load_session():
            tk.Button(
                button_frame, 
                text="Quick Login", 
                bg="#e1f5fe", 
                command=self.handle_quick_login
            ).pack(side=tk.LEFT, padx=10)

        # 🔑 Bind the Enter/Return key to the login handler
        self.root.bind('<Return>', lambda event: self.handle_login())

        self.root.mainloop()

    def handle_quick_login(self):
        """Re-enters the app using existing session."""
        from utils.session import Session
        user = Session.get_user()
        if user:
            messagebox.showinfo("Quick Login", f"Welcome back, {user.username}!")
            self.root.destroy()
            MainWindow()
        else:
            messagebox.showerror("Error", "Session expired or invalid.")

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
