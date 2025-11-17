# right_panel.py
import tkinter as tk
from tkinter import ttk
from views.table.table_view import TableView
import importlib
from utils.debug import print_r
import traceback


class RightPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#ffffff", *args, **kwargs)
        self.pack_propagate(False)
        self.render_default()

    def render_default(self):
        self.clear()
        tk.Label(
            self, text="Welcome to the Right Panel", bg="#ffffff", font=("Arial", 12)
        ).pack(pady=20)

    def render_content(self, nav_name, ctrlName, navigation_name):
        self.clear()

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

        except Exception as e:
            # Print full traceback for detailed info
            print("Error loading content:", e)
            traceback.print_exc()
            tk.Label(self, text=f"Error loading: {str(e)}", fg="red", bg="#ffffff").pack(pady=20)
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
