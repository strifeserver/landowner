import logging
import sys
import traceback
from controllers.AuthController import AuthController
from views.login.login_view import LoginView  # <- updated import

from utils.session import Session
from views.main_window import MainWindow

# Setup logging
logging.basicConfig(
    filename='python.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Uncaught exception:\n%s", error_msg)
    print(error_msg, file=sys.stderr)

# Install exception handler
sys.excepthook = handle_exception

def run_migrations():
    """Run database migrations silently on startup."""
    try:
        import migrate
        migrate.main()
    except Exception as e:
        logging.error(f"Migration error on startup: {str(e)}")

if __name__ == "__main__":
    run_migrations()
    try:
        # ALWAYS show login view on startup as requested
        LoginView(AuthController)
    except Exception:
        logging.error("Final catch-all for application crash:\n%s", traceback.format_exc())
        raise
