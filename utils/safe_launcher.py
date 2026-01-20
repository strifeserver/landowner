import tkinter as tk
from tkinter import messagebox
import traceback
from utils.debug import print_r

def safe_launch(callable_obj, *args, **kwargs):
    """
    Safely invokes a callable (like a Class constructor or a function) to open a window.
    Captures any exceptions during the process and displays a user-friendly error dialog.
    """
    try:
        return callable_obj(*args, **kwargs)
    except Exception as e:
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        
        print(f"!!! SAFE LAUNCH EXCEPTION !!!\n{full_traceback}")
        
        messagebox.showerror(
            "System Error",
            f"An error occurred while opening the window.\n\nError: {error_msg}\n\nPlease contact support."
        )
        return None
