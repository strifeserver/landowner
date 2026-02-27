import threading
import tkinter as tk
from functools import wraps

class ThreadManager:
    """
    Manages background threads and UI callbacks.
    """
    def __init__(self, ui_master=None):
        self.ui_master = ui_master

    def run_in_thread(self, target, callback=None, error_callback=None, *args, **kwargs):
        """
        Runs 'target' function in a separate thread.
        'callback' is called with the result of 'target' on the main thread.
        'error_callback' is called with the exception if 'target' fails.
        """
        def thread_target():
            try:
                result = target(*args, **kwargs)
                if callback:
                    self._schedule_on_main(lambda: callback(result))
            except Exception as e:
                import traceback
                traceback.print_exc()
                if error_callback:
                    self._schedule_on_main(lambda: error_callback(e))
                else:
                    # Default error handling
                    self._schedule_on_main(lambda: self._default_error_handler(e))

        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()
        return thread

    def _schedule_on_main(self, task):
        if self.ui_master:
            self.ui_master.after(0, task)
        else:
            # Fallback if no UI context (might not run if loop is not active or safe)
            task()

    def _default_error_handler(self, exception):
        print(f"Background thread error: {exception}")
        # Could show a messagebox here if we had tk imported safely
