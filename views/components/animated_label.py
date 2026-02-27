import tkinter as tk

class AnimatedLabel(tk.Label):
    """A Label that can display an animated GIF using ImageManager for caching."""
    def __init__(self, master, file_path, size=(150, 150), **kwargs):
        super().__init__(master, **kwargs)
        try:
            from utils.ImageManager import ImageManager
            self.frames, self.delay = ImageManager.get_gif(file_path, size)
        except ImportError:
            # Fallback if ImageManager is not found or fails
            self.frames = []
            self.delay = 100
        
        self.idx = 0
        self._after_id = None
        self._is_animating = False
        
        if self.frames:
            self.config(image=self.frames[0])
            if len(self.frames) > 1:
                self.animate()
                # Bind visibility events to pause/resume animation
                self.bind("<Map>", self._resume_animation)
                self.bind("<Unmap>", self._pause_animation)
        
        self.bind("<Destroy>", lambda e: self.stop_animation())

    def animate(self):
        if not self.winfo_exists() or not self.frames:
            return
            
        # If not viewable, stop the loop (it will affect restart on Map)
        if not self.winfo_viewable():
            self._is_animating = False
            return

        self._is_animating = True
        self.idx = (self.idx + 1) % len(self.frames)
        try:
            self.config(image=self.frames[self.idx])
            self._after_id = self.after(self.delay, self.animate)
        except:
            pass

    def _resume_animation(self, event=None):
        """Resume animation when window is shown again."""
        if not self._is_animating and self.frames and len(self.frames) > 1:
            self.animate()

    def _pause_animation(self, event=None):
        """Pause animation when window is hidden."""
        pass

    def stop_animation(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except:
                pass
            self._after_id = None
            self._is_animating = False
