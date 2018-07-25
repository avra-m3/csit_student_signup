import tkinter as tk

from PIL import Image, ImageTk


class OutputPane(tk.Frame):
    placeholder = Image.open("./resources/placeholder.jpg")

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid(row=0, column=1, rowspan=2)

        self.str_status = tk.StringVar("")
        self.im_output = None

        self.st_label = tk.Label(self, textvariable=self.str_status)
        self.im_label = tk.Label(self)

        self.st_label.grid()
        self.im_label.grid(row=1)

        self.reset()

    def update_status(self, state):
        self.str_status.set(str(state))

    def update_image(self, image: Image):
        image.thumbnail((700, 400), Image.ANTIALIAS)
        self.im_output = ImageTk.PhotoImage(image)
        self.im_label.configure(image=self.im_output)
        self.im_label.grid()

    def reset(self):
        self.update_status("Starting")
        self.update_image(self.placeholder)