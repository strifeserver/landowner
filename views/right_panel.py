# right_panel.py
import tkinter as tk
from tkinter import ttk
from views.table.table_view import TableView
import importlib
from utils.debug import print_r
import traceback
from datetime import datetime
import tkinter.font as tkFont
import os 
from helpers.helpers import get_controller



class RightPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#ffffff", *args, **kwargs)
        self.pack_propagate(False)
        self._after_ids = {} # Track timers for cleanup
        self.bind("<Destroy>", lambda e: self.stop_timers())
        self.render_default()

    def stop_timers(self):
        """Cancel all pending after() calls."""
        if hasattr(self, "_after_ids"):
            for name, after_id in list(self._after_ids.items()):
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
            self._after_ids.clear()
        

    # -------------------------------
    # DEFAULT PANEL WITH MEMORY LABEL
    # -------------------------------
    def render_default(self):
        self.clear()

        # Row 1 — Welcome Label
        tk.Label(self, text="Welcome to the Right Panel", font=("Arial", 12)).pack(pady=(20, 5))




    def render_content(self, nav_name, ctrlName, navigation_name):
        self.clear()
        self.create_top_right_account()

        try:
            controller_class = get_controller(ctrlName)

            # Check if controller provides a custom view
            if hasattr(controller_class, "index_view"):
                view = controller_class.index_view(self)
                view.pack(fill=tk.BOTH, expand=True)
                self.create_footer()
                return

            # Fetch initial result (page 1)
            initial_result = controller_class.index(
                filters={}, pagination=True, items_per_page=10, page=1
            )

            if initial_result is not None:
                data_list = initial_result["data"] if isinstance(initial_result, dict) else initial_result
                
                # Try to get model class from data or controller
                model_class = None
                if data_list:
                    model_class = data_list[0].__class__
                elif hasattr(controller_class, "model"):
                    model_class = controller_class.model

                if not model_class:
                    if not data_list:
                        tk.Label(self, text="No data found", bg="#ffffff").pack(pady=20)
                        self.create_footer()
                        return
                    else:
                        # Fallback for data without model class
                        sample = data_list[0].__dict__ if hasattr(data_list[0], "__dict__") else data_list[0]
                        visible_fields = [(field, field.replace("_", " ").title()) for field in sample.keys()]
                else:
                    # Use get_visible_fields from model class
                    if hasattr(model_class, "get_visible_fields") and callable(getattr(model_class, "get_visible_fields")):
                        visible_fields = model_class.get_visible_fields()
                    else:
                        # Fallback: auto-generate visible fields from model attributes
                        sample = data_list[0].__dict__ if data_list else {}
                        visible_fields = [(field, field.replace("_", " ").title()) for field in sample.keys()]

                columns = [field for field, _ in visible_fields]
                column_labels = [alias for _, alias in visible_fields]

                # Convert objects → dicts
                data = [obj.__dict__ for obj in data_list] if data_list and hasattr(data_list[0], "__dict__") else []

                # Fetch Navigation ID to pass to TableView for permissions
                from models.navigation import Navigation
                nav_item = None
                try:
                    # navigation column matches nav_name passed from main_window
                    navs = Navigation.index(filters={"navigation": nav_name})
                    if navs:
                        nav_item = navs[0]
                except Exception as e:
                    pass

                # Create Table
                table = TableView(
                    self,
                    columns=columns,
                    column_labels=column_labels,
                    data=data,
                    controller_callback=None,  # Added later
                    title=navigation_name,
                    nav_id=nav_item.id if nav_item else None, # Pass ID
                    table_name=model_class.table_name if model_class and hasattr(model_class, "table_name") else None
                )
                table.pack(fill=tk.BOTH, expand=True)
                table.controller_class = controller_class

                # ------------------------------------------
                # 2. PAGINATION CALLBACK
                # ------------------------------------------
                def controller_callback(
                    filters=None,
                    searchAll=None,
                    pagination=False,
                    items_per_page=10,
                    page=1,
                    **kwargs
                ):
                    try:
                        result = controller_class.index(
                            filters=filters,
                            pagination=True,
                            items_per_page=items_per_page,
                            page=page,
                            searchAll=searchAll,
                        )

                        table.total_rows = result.get("total_rows", 0)
                        table.total_pages = result.get("total_pages", 1)
                        table.last_page = result.get("last_page", 1)

                        
                        return result["data"]

                    except Exception as err:
                        table.total_rows = 0
                        table.total_pages = 1
                        table.last_page = 1
                        return []

                table.controller_callback = controller_callback
                
                if isinstance(initial_result, dict):
                    table.total_rows = initial_result.get("total_rows", 0)
                    table.total_pages = initial_result.get("total_pages", 1)
                    table.last_page = initial_result.get("last_page", 1)
                
                table.render_rows()
            else:
                tk.Label(self, text="No data found", bg="#ffffff").pack(pady=20)

        except Exception as e:
            tk.Label(self, text=f"Error loading: {str(e)}", fg="red", bg="#ffffff").pack(pady=20)

        self.create_footer()

            
            
    def clear(self):
        self.stop_timers()
        for widget in self.winfo_children():
            # Check if widget has a custom cleanup method
            if hasattr(widget, "cleanup") and callable(widget.cleanup):
                try:
                    widget.cleanup()
                except Exception as e:
                    print(f"Cleanup error for {widget}: {e}")
            widget.destroy()
        
        self.stop_timers()  # Ensure timers are stopped when clearing panel
        
        # Proactive Garbage Collection after clearing content
        import gc
        gc.collect()


    def create_footer(self):
        font_size = 8

        # System default background (native)
        sys_bg = tk.Frame().cget("bg")  # 'SystemButtonFace' on Windows

        # --- HR / Divider above footer ------------------------------------

        divider = ttk.Separator(self, orient="horizontal")
        divider.pack(side=tk.TOP, fill="x")  # Sits right above the footer

        # --- Footer Outer Frame (to avoid white padding) -------------------
        padded_frame = tk.Frame(self, bg=sys_bg)
        padded_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Inner footer frame (actual content)
        footer_frame = tk.Frame(padded_frame, bg=sys_bg)
        footer_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Left label (Settings Based)
        from models.Setting import Setting
        copy_set = Setting.index(filters={"setting_name": "copyright"})
        copyright_text = copy_set[0].setting_value if copy_set else "LandOwner © 2025"

        tk.Label(
            footer_frame,
            text=copyright_text,
            font=("Arial", font_size),
            bg=sys_bg
        ).pack(side=tk.LEFT)

        # Right memory label
        self.memory_label = tk.Label(
            footer_frame,
            font=("Arial", font_size),
            bg=sys_bg
        )
        self.memory_label.pack(side=tk.RIGHT)

        # Start updating memory every second
        self.update_memory_usage()

        
    def update_memory_usage(self):
        pass


    def create_top_right_account(self):
        """
        Creates a top-right 'My Account' button with a live datetime label below it,
        10px spacing from the top, and a solid gray horizontal line below.
        """
        
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        btn_font = tkFont.Font(family="Arial", size=12, weight="bold")
        
        # My Account button
        self.prev_btn = tk.Button(
            top_frame,
            text="My Account",
            command=lambda: self.render_content("my_account", "MyAccountController", "My Account"),
            font=btn_font,
            padx=15,
            pady=5
        )
        self.prev_btn.pack(side=tk.RIGHT, padx=15, pady=(5, 3))
        
        # Date/Time label
        self.datetime_label = tk.Label(
            top_frame,
            font=("Arial", 10),
            justify='right'
        )
        self.datetime_label.pack(side=tk.RIGHT, padx=10, pady=(0, 0))

        # Function to update the datetime label
        def update_datetime():
            if not self.winfo_exists():
                return
            try:
                now = datetime.now()
                date_str = now.strftime("%m/%d/%Y")
                time_str = now.strftime("%I:%M %p")
                if hasattr(self, 'datetime_label') and self.datetime_label.winfo_exists():
                    self.datetime_label.config(text=f"{date_str}\n{time_str}")
                
                # Re-schedule and store ID
                self._after_ids['datetime'] = self.after(1000, update_datetime)
            except Exception:
                pass

        update_datetime()  # start the timer
        
        

        # System default background (native)
        sys_bg = tk.Frame().cget("bg")  # 'SystemButtonFace' on Windows

        # --- HR / Divider above footer ------------------------------------

        divider = ttk.Separator(self, orient="horizontal")
        divider.pack(side=tk.TOP, fill="x")  # Sits right above the footer

        # --- Footer Outer Frame (to avoid white padding) -------------------
        padded_frame = tk.Frame(self, bg=sys_bg)
        padded_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Inner footer frame (actual content)
        footer_frame = tk.Frame(padded_frame, bg=sys_bg)
        footer_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)


        
        
        
        
        
        
        
        # sys_bg = tk.Frame().cget("bg")  
        
        # # Spacer frame for top padding (10px)
        # # spacer = tk.Frame(self, height=10, bg=sys_bg)
        # # spacer.pack(side=tk.TOP, fill=tk.X)
        
        # # Spacer frame for top padding (10px)
        # # spacer_bottom = tk.Frame(self, height=10, bg=sys_bg)
        # # spacer_bottom.pack(side=tk.BOTTOM, fill=tk.X)


        # # Top frame (stretch across top)
        # top_frame = tk.Frame(self)
        # top_frame.pack(side=tk.TOP, fill=tk.X)

        # # Font for button
        # btn_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        # # My Account button
        # self.prev_btn = tk.Button(
        #     top_frame,
        #     text="My Account",
        #     command=lambda: print("TEST"),
        #     font=btn_font,
        #     padx=15,
        #     pady=5
        # )
        # self.prev_btn.pack(side=tk.RIGHT, padx=10, pady=(0, 0))
        


        # # Date/Time label
        # self.datetime_label = tk.Label(
        #     top_frame,
        #     font=("Helvetica", 10),
        #     justify='right'
        # )
        # self.datetime_label.pack(side=tk.RIGHT, padx=10, pady=(0, 0))

        # # Function to update the datetime label
        # def update_datetime():
        #     now = datetime.now()
        #     date_str = now.strftime("%m/%d/%Y")
        #     time_str = now.strftime("%I:%M %p")
        #     self.datetime_label.config(text=f"{date_str}\n{time_str}")
        #     self.datetime_label.after(1000, update_datetime)  # update every second

        # update_datetime()  # start the timer
        
        #     # --- HR / Divider below top section -----------------------------------
        # divider = ttk.Separator(self, orient="horizontal")
        # divider.pack(side=tk.TOP, fill="x", pady=(10, 0))  # nice breathing space
