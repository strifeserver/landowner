# main_window.py
import tkinter as tk
from tkinter import messagebox
from models.navigation import Navigation
from models.setting import Setting
from views.right_panel import RightPanel  # Import the new RightPanel


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LandOwner - Main Window")
        WindowSize = Setting.index(filters={"setting_name": "window_size"})
        if WindowSize["data"]:  # make sure there's at least one row
            self.root.geometry(WindowSize["data"][0].setting_value)
        else:
            self.root.geometry("800x600")  # fallback size

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Left frame (navigation)
        left_frame = tk.Frame(self.root, bg="#e0e0e0", width=160)
        left_frame.grid(row=0, column=0, sticky="nswe")

        tk.Label(
            left_frame, text="Navigation", bg="#e0e0e0", font=("Arial", 10, "bold")
        ).pack(pady=10)
        self.load_navigation(left_frame)

        # Right frame (content)
        self.right_panel = RightPanel(self.root, width=640)
        self.right_panel.grid(row=0, column=1, sticky="nswe")

        self.root.mainloop()

    def load_navigation(self, parent_frame):
        menu_items = Navigation.index()
        for item in menu_items['data']:
            
            btn = tk.Button(
                parent_frame,
                text=item.menu_name,
                width=20,
                command=lambda name=item.navigation,
                ctrl=item.controller, navigation_name=item.menu_name: self.on_menu_click(name, ctrl, navigation_name),
            )
            btn.pack(pady=5)

    def on_menu_click(self, name, controller_name, navigation_name):
        # Instead of messagebox, update the right panel
        self.right_panel.render_content(name, controller_name, navigation_name)
