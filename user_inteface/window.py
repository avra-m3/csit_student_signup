import tkinter as tk

import cv2
from PIL import Image, ImageTk


class Window(tk.Frame):
    def __init__(self, master, config, **kw):
        super().__init__(master, **kw)
        self.pack()
        self.status_str = tk.StringVar()
        self.config = config
        self.image = None
        self.camera = None
        self.btn_continue = None
        self.last_capture = None
        self.btn_save = None
        self.label_info = None
        self.status = tk.Message(self, textvariable=self.status_str)

        self.on_continue = self.hide_result
        self.on_save = None

        self.status.grid()

    def update_camera(self, cv2_image) -> None:
        """
        Call this to update the camera with a cv2 image object
        :param cv2_image: A cv2 Image
        :return: None
        """
        self.last_capture = cv2_image
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        cv2_image = Image.fromarray(cv2_image)
        self.set_camera(cv2_image)

    def set_camera(self, raw: Image) -> None:
        """
        Used internally to update the camera image with an Image Object
        :param raw: The new PIL image to set the camera to
        :return: None
        """
        if self.camera is None:
            self.camera = tk.Label(self)
            self.camera.grid(row=0, column=0)
        self.camera.raw = raw
        if self.image is not None:
            raw = raw.resize((160, 120), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(raw)
        self.camera.configure(image=image)
        self.camera.image = image

    def update_prelim(self, result_image) -> None:
        """
        Call this function with a cv2 image to update the "result" image
        Will create a label for the result if one does not exist.
        :param result_image: A CV2 image object
        :return: None
        """
        raw_img = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        raw_img = Image.fromarray(raw_img)
        if self.image is None:
            self.image = tk.Label(self)
            self.image.grid(row=0, column=1, rowspan=4)
            self.set_camera(self.camera.raw)
        image = ImageTk.PhotoImage(raw_img)

        self.image.configure(image=image)
        self.image.raw = image

    def hide_result(self) -> None:
        """
        Call this to wipe the current result image from existence and resize the camera
        :return: None
        """
        if self.image is not None:
            self.image.grid_forget()
            self.image = None
        if self.btn_continue is not None:
            self.btn_continue.grid_forget()
            self.btn_continue = None
        if self.label_info is not None:
            self.label_info.grid_forget()
            self.label_info = None
        self.set_camera(self.camera.raw)

    def update_result(self, state, image=None) -> None:
        """
        Update Image and card information
        :param state:
        :param card: A Card object used to get information about the result
        :param image: The cv2 image to display
        :return: None
        """
        if image is None:
            image = state.frame
            card = state.card
        else:
            card = state
        self.hide_result()
        self.update_prelim(image)
        self.btn_continue = tk.Button(self, text="Continue", command=self.on_continue)
        if self.on_save is not None:
            self.btn_save = tk.Button(self, text="Save Record", command=self.on_save)
            self.btn_save.grid(row=2, sticky=tk.E + tk.W)
        student_id = str(card.get_student_id())
        if card.is_valid():
            name = " ".join([str(c) for c in card.get_names()])
            label_str = """
Results:
Student ID: {student_id}
Full Name: {name}
            """.format(student_id=student_id, name=name)
        else:
            label_str = """
            An error occurred while retrieving the results: {error}
            """.format(error=str(card.errors))
        self.label_info = tk.Label(self, text=label_str, justify="left", wraplength=200)
        self.label_info.card = card
        self.label_info.grid(row=1, sticky=tk.E + tk.W)
        self.btn_continue.grid(row=3, sticky=tk.E + tk.W)
