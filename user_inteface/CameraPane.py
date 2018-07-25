import tkinter as tk

from PIL import Image, ImageTk


class CameraPane(tk.Frame):
    placeholder = Image.open("./resources/placeholder.jpg")
    CAMERA_DIM = (160, 120)

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid(row=0, column=0)
        self._cam = None
        self._debug = None

        self.cm_label = tk.Label(self)
        self.dg_label = tk.Label(self)

        self.cm_label.grid(sticky=tk.N)
        self.dg_label.grid(row=1, sticky=tk.N)

        self.set(self.placeholder, self.placeholder)

    def set(self, camera, debug=None):
        camera = camera.copy()
        camera.thumbnail((160, 120), Image.ANTIALIAS)
        self._cam = ImageTk.PhotoImage(camera)
        self.cm_label.configure(image=self._cam)
        if debug is not None:
            debug = debug.copy()
            debug.thumbnail((160, 120), Image.ANTIALIAS)
            self._debug = ImageTk.PhotoImage(debug)
            self.dg_label.configure(image=self._debug)