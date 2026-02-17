import tkinter as tk
from PIL import Image, ImageTk
import os

class ImageManager:
    """
    Singleton utility to manage and cache images and GIFs to minimize memory usage 
    and redundant disk I/O.
    """
    _static_cache = {}    # {path: PhotoImage}
    _gif_cache = {}       # {path: [PhotoImage, ...]}
    _metadata = {}        # {path: {'delay': int}}
    _last_root = None     # Track the Tk root to avoid invalid pyimage references

    @staticmethod
    def _check_root():
        """
        Internal check to ensure cache is valid for the current Tk root.
        Tkinter images are tied to the root that created them.
        """
        current_root = tk._default_root
        if current_root != ImageManager._last_root:
            # Root has changed (e.g. after logout and new login)
            # Clear cache to prevent "pyimage" doesn't exist errors.
            ImageManager.clear_cache()
            ImageManager._last_root = current_root

    @staticmethod
    def get_static(path, size=None):
        """Loads and caches a static image."""
        ImageManager._check_root()
        cache_key = (path, size)
        if cache_key in ImageManager._static_cache:
            return ImageManager._static_cache[cache_key]

        try:
            if not os.path.exists(path):
                return None
                
            img = Image.open(path)
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            ImageManager._static_cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"ImageManager Error (Static): {e}")
            return None

    @staticmethod
    def get_gif(path, size=None):
        """Loads and caches all frames of an animated GIF."""
        ImageManager._check_root()
        cache_key = (path, size)
        if cache_key in ImageManager._gif_cache:
            return ImageManager._gif_cache[cache_key], ImageManager._metadata.get(cache_key, {}).get('delay', 100)

        try:
            if not os.path.exists(path):
                return [], 100

            frames = []
            delay = 100
            
            with Image.open(path) as img:
                delay = img.info.get('duration', 100)
                try:
                    while True:
                        frame = img.copy()
                        if size:
                            frame.thumbnail(size, Image.Resampling.LANCZOS)
                        frames.append(ImageTk.PhotoImage(frame))
                        img.seek(len(frames))
                except EOFError:
                    pass
            
            ImageManager._gif_cache[cache_key] = frames
            ImageManager._metadata[cache_key] = {'delay': delay}
            return frames, delay
        except Exception as e:
            print(f"ImageManager Error (GIF): {e}")
            return [], 100

    @staticmethod
    def clear_cache():
        """Clears all cached images to free memory."""
        ImageManager._static_cache.clear()
        ImageManager._gif_cache.clear()
        ImageManager._metadata.clear()
