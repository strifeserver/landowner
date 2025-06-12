# main.py
from controllers.auth_controller import AuthController
from views.login.login_view import LoginView  # <- updated import

if __name__ == "__main__":
    controller = AuthController()
    LoginView(controller)
