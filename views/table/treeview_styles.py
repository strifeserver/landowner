from tkinter import ttk

def apply_treeview_style(configure_styles):
    style = ttk.Style()
    style.theme_use("default")

    #Table style Config
    # table_height = 10
    # table_heading_font_size = 12
    # table_row_font_size = 11
    # table_font = "Arial"
    # table_row_height = 30
    #Table style Config
        # style = ttk.Style()
        # style.configure("Custom.Treeview", rowheight=table_row_height)
        # tree_font = (table_font, table_row_font_size) 
        # style.configure("Custom.Treeview", font=tree_font)
        # style.configure("Custom.Treeview.Heading", font=(table_font, table_heading_font_size, "bold"))


    style.configure(
        "Custom.Treeview",
        background="white",
        foreground="black",
        rowheight=configure_styles['table_row_height'],
        font=(configure_styles['table_font'], configure_styles['table_row_font_size']),
        fieldbackground="white",
        bordercolor="black",
        borderwidth=1,
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", "#e1e5f2")],
        foreground=[("selected", "black")],
    )
    style.configure(
        "Custom.Treeview.Heading",
        background="black",
        foreground="white",
        font=(configure_styles['table_font'], configure_styles['table_heading_font_size'], "bold"),
        borderwidth=1,
    )
    style.layout(
        "Custom.Treeview",
        [
            (
                "Treeview.field",
                {
                    "sticky": "nswe",
                    "border": "1",
                    "children": [
                        (
                            "Treeview.padding",
                            {
                                "sticky": "nswe",
                                "children": [
                                    ("Treeview.treearea", {"sticky": "nswe"})
                                ],
                            },
                        )
                    ],
                },
            )
        ],
    )
