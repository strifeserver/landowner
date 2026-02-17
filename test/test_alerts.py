import sys
import os
import os.path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from utils.alert import Alert

def test_alerts():
    root = tk.Tk()
    root.withdraw() # Hide main window

    print("Testing Success Alert...")
    Alert.success("This is a success message!", "Success")

    print("Testing Error Alert with dict...")
    Alert.error({"username": ["is required", "must be 5 chars"], "email": "invalid format"}, "Validation Errors")

    print("Testing Confirmation Alert...")
    def on_confirm():
        print("Confirmed!")
        Alert.success("You clicked Save!")
        
    def on_cancel():
        print("Cancelled!")
        Alert.info("You clicked Cancel!")

    Alert.confirm("Do you want to save these changes?", on_confirm=on_confirm, on_cancel=on_cancel)

    root.mainloop()

if __name__ == "__main__":
    test_alerts()
