import os
import sys

# Get the absolute path to the project root
# This file is in cms/utils/paths.py, so we go up one level
# When frozen by PyInstaller, use sys._MEIPASS for bundled assets
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    ROOT_DIR = sys._MEIPASS
else:
    # Running as script
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main Assets Directory (Bundled with exe)
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

# Persistent Data Directory (External to exe, alongside it)
if getattr(sys, 'frozen', False):
    # Running as compiled executable - Data is alongside the EXE
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    # Running as script
    DATA_DIR = os.path.join(ROOT_DIR, "data")

if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except:
        pass

# Persistent Uploads Directory
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
if not os.path.exists(PROFILES_DIR):
    try:
        os.makedirs(PROFILES_DIR, exist_ok=True)
    except:
        pass



# Sub-folders
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
GIFS_DIR = os.path.join(ASSETS_DIR, "gifs")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

def get_asset_path(subfolder, filename):
    """
    Returns the absolute path to an asset.
    Example: get_asset_path("gifs", "loading.gif")
    """
    return os.path.join(ASSETS_DIR, subfolder, filename)

def get_gif_path(filename):
    """Returns absolute path to a GIF file."""
    return os.path.join(GIFS_DIR, filename)

def get_image_path(filename):
    """Returns absolute path to an image file."""
    return os.path.join(IMAGES_DIR, filename)
