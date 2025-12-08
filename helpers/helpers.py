import importlib

def get_controller(nav_name, ctrl_name):
    """
    Dynamically import a controller class, handling snake_case or PascalCase filenames and class names.

    ```
    nav_name: name used for the file (e.g., 'settings')
    ctrl_name: class name (e.g., 'SettingsController')
    """
    # Possible module names
    module_variants = [f"{nav_name}_controller", f"{nav_name.capitalize()}Controller"]

    for module_name in module_variants:
        try:
            module = importlib.import_module(f"controllers.{module_name}")
            
            # Possible class names
            class_variants = [ctrl_name, ''.join(word.capitalize() for word in ctrl_name.split('_'))]
            
            for cls_name in class_variants:
                if hasattr(module, cls_name):
                    return getattr(module, cls_name)
        except ModuleNotFoundError:
            continue

    raise ImportError(f"Controller '{ctrl_name}' not found for nav '{nav_name}'.")
   

    # Usage in any other file:

    # from helpers import get_controller

    # controller_class = get_controller('settings', 'SettingsController')

    # controller_instance = controller_class()
