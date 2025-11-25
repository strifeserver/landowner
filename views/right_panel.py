# right_panel.py
import tkinter as tk
from tkinter import ttk
from views.table.table_view import TableView
import importlib
from utils.debug import print_r
import traceback
from datetime import datetime
import tkinter.font as tkFont
import psutil, os 

class RightPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#ffffff", *args, **kwargs)
        self.pack_propagate(False)
        self.render_default()
        

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
        # top_frame = tk.Frame(self)
        # top_frame.pack(side=tk.TOP, fill=tk.X)  # stretch across top
        # self.prev_btn = tk.Button(
        #     top_frame,
        #     text="My Account",
        #     command=lambda: print("TEST"),
        #     padx=15,  # horizontal padding inside button
        #     pady=5    # vertical padding inside button
        # )
        # # Pack to the right
        # self.prev_btn.pack(side=tk.RIGHT, padx=10, pady=5)
               
        try:
            controller_name = f"{nav_name}_controller"
            controller_module = importlib.import_module(f"controllers.{controller_name}")
            controller_class = getattr(controller_module, ctrlName)

            # Fetch initial result (page 1)
            initial_result = controller_class.index(
                filters={}, pagination=True, items_per_page=10, page=1
            )

            if initial_result:
                model_class = initial_result["data"][0].__class__ if isinstance(initial_result, dict) else initial_result[0].__class__
                visible_fields = model_class.get_visible_fields()
                columns = [field for field, _ in visible_fields]
                column_labels = [alias for _, alias in visible_fields]
                data = [obj.__dict__ for obj in initial_result["data"]] if isinstance(initial_result, dict) else [obj.__dict__ for obj in initial_result]

                table = TableView(
                    self,
                    columns=columns,
                    column_labels=column_labels,
                    data=data,
                    controller_callback=None,  # Temporarily None
                    title=navigation_name,
                )
                table.pack(fill=tk.BOTH, expand=True)
                table.controller_class = controller_class  # Keep reference

                # Now define controller_callback with access to the table instance
                def controller_callback(filters=None, searchAll=None, page=1):
                    try:
                        result = controller_class.index(
                            filters=filters,
                            pagination=True,
                            items_per_page=10,
                            page=page,
                            searchAll=searchAll,
                        )

                        # Save pagination info to TableView instance
                        table.total_rows = result.get("total_rows", 0)
                        table.total_pages = result.get("total_pages", 1)
                        table.last_page = result.get("last_page", 1)

                        # Return only the data for Treeview
                        return [obj.__dict__ for obj in result["data"]]

                    except Exception as err:
                        print("Filter error:", err)
                        table.total_rows = 0
                        table.total_pages = 1
                        table.last_page = 1
                        return []

                # Assign the callback now that table exists
                table.controller_callback = controller_callback
                table.render_rows()  # Render first page

            else:
                tk.Label(self, text="No data found", bg="#ffffff").pack(pady=20)
            
            self.create_footer()
            
        except Exception as e:
            # Print full traceback for detailed info
            print("Error loading content:", e)
            traceback.print_exc()
            tk.Label(self, text=f"Error loading: {str(e)}", fg="red", bg="#ffffff").pack(pady=20)
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


    def create_footer(self):
        font_size = 8
        # System default background
        sys_bg = tk.Frame().cget("bg")  # 'SystemButtonFace' on Windows
        # Outer frame to control padding (no visible bg change)
        padded_frame = tk.Frame(self, bg=sys_bg)
        padded_frame.pack(side=tk.BOTTOM, fill=tk.X)
        # Inner footer frame
        footer_frame = tk.Frame(padded_frame, bg=sys_bg)
        footer_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Left label
        tk.Label(footer_frame, text="Landowner©2025", font=("Arial", font_size), bg=sys_bg).pack(side=tk.LEFT)
        
        # Right memory label
        self.memory_label = tk.Label(footer_frame, font=("Arial", font_size), bg=sys_bg)
        self.memory_label.pack(side=tk.RIGHT)
        self.update_memory_usage()
        
    def update_memory_usage(self):
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / (1024 * 1024)
        self.memory_label.config(text=f"Memory Usage: {mem_mb:.2f} MB")
        self.memory_label.after(1000, self.update_memory_usage)  # update again in 1 sec


    def create_top_right_account(self):
        """
        Creates a top-right 'My Account' button with a live datetime label below it,
        10px spacing from the top, and a solid gray horizontal line below.
        """
        # Spacer frame for top padding (10px)
        spacer = tk.Frame(self, height=10)
        spacer.pack(side=tk.TOP, fill=tk.X)
        
        # Spacer frame for top padding (10px)
        spacer_bottom = tk.Frame(self, height=10)
        spacer_bottom.pack(side=tk.BOTTOM, fill=tk.X)


        # Top frame (stretch across top)
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Font for button
        btn_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        # My Account button
        self.prev_btn = tk.Button(
            top_frame,
            text="My Account",
            command=lambda: print("TEST"),
            font=btn_font,
            padx=15,
            pady=5
        )
        self.prev_btn.pack(side=tk.RIGHT, padx=10, pady=(0, 0))
        


        # Date/Time label
        self.datetime_label = tk.Label(
            top_frame,
            font=("Helvetica", 10),
            justify='right'
        )
        self.datetime_label.pack(side=tk.RIGHT, padx=10, pady=(0, 0))

        # Function to update the datetime label
        def update_datetime():
            now = datetime.now()
            date_str = now.strftime("%m/%d/%Y")
            time_str = now.strftime("%I:%M %p")
            self.datetime_label.config(text=f"{date_str}\n{time_str}")
            self.datetime_label.after(1000, update_datetime)  # update every second

        update_datetime()  # start the timer

        # --- Solid gray horizontal line ---
        # --- Solid gray horizontal line with 10px top and bottom padding ---
        # gray_line = tk.Frame(self, height=2, bg="#a0a0a0")  # 2px height, gray color
        # gray_line.pack(side=tk.TOP, fill=tk.X, pady=10)  # 10px spacing top and bottom