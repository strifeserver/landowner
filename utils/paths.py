import os

# Get the absolute path to the project root
# This file is in landowner/utils/paths.py, so we go up one level
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main Assets Directory
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

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
