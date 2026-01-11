import importlib

def get_controller(ctrl_name):
    """
    Dynamically import a controller class where:
    - File name == Class name (PascalCase)
    - Example: UsersController.py -> class UsersController
    """
    try:
        module = importlib.import_module(f"controllers.{ctrl_name}")
    except ModuleNotFoundError as e:
        raise ImportError(f"Controller module '{ctrl_name}.py' not found.") from e

    try:
        return getattr(module, ctrl_name)
    except AttributeError as e:
        raise ImportError(
            f"Class '{ctrl_name}' not found in '{ctrl_name}.py'."
        ) from e
