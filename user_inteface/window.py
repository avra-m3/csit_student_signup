import tkinter as tk

from PIL import Image, ImageTk

from functions import cv_2_pil
from user_inteface.ErrorDialog import ErrorDialog


class Window(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid()
        self.output = OutputPane(master)
        self.camera = CameraPane(master)
        self.record = RecordPanel(master)

    def update_camera(self, frame, frame_debug):
        frame = cv_2_pil(frame)
        frame_debug = cv_2_pil(frame_debug)
        self.camera.set(frame, frame_debug)

    def update_prelim(self, image):
        image = cv_2_pil(image)
        self.output.update_image(image)

    def update_result(self, card, image, success, cancel):
        if card is None:
            ErrorDialog(self, "The card was not valid.", image, "Processing error")
            self.reset()
            return
        self.record.set(card.get_name(), card.get_student_id(), success, cancel)

    def reset(self):
        self.output.reset()
        self.record.disable()


class OutputPane(tk.Frame):
    placeholder = Image.open("./resources/placeholder.jpg")

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid(row=0, column=1, rowspan=2)

        self._status = tk.StringVar("")
        self._image = None

        self.st_label = tk.Label(self, textvariable=self._status)
        self.im_label = tk.Label(self)

        self.st_label.grid()
        self.im_label.grid(row=1)

        self.reset()

    def update_status(self, state):
        self._status.set(str(state))

    def update_image(self, image: Image):
        image.thumbnail((self.winfo_screenwidth() / 2, self.winfo_screenheight() * .75), Image.ANTIALIAS)
        self._image = ImageTk.PhotoImage(image)
        self.im_label.configure(image=self._image)
        self.im_label.grid()

    def reset(self):
        self.update_status("Starting")
        self.update_image(self.placeholder)


class RecordPanel(tk.Frame):
    save_icon = Image.open("resources/iconsave.png")
    remove_icon = Image.open("resources/icontrash.png")

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid(row=1, column=0, sticky=("N", "S", "E", "W"))
        self._name = tk.StringVar()
        self._id = tk.StringVar()

        self.output_panel = tk.LabelFrame(self)
        self.id_label = tk.Label(self.output_panel, textvariable=self._id, justify="left")
        self.nm_label = tk.Label(self.output_panel, textvariable=self._name, justify=tk.LEFT)

        self.save_icon.thumbnail((80, 70), Image.ANTIALIAS)
        self.remove_icon.thumbnail((80, 70), Image.ANTIALIAS)

        self._sv_icn = ImageTk.PhotoImage(self.save_icon)
        self._rm_icn = ImageTk.PhotoImage(self.remove_icon)
        self.sv_button = tk.Button(self, image=self._sv_icn)
        self.cc_button = tk.Button(self, image=self._rm_icn)

        self.id_label.grid(sticky=("N", "S", "E", "W"))
        self.nm_label.grid(row=1, sticky=("N", "S", "E", "W"))
        #
        # self.sv_button.grid(row=2, sticky=("N", "S", "E", "W"))
        # self.cc_button.grid(row=2, column=1, sticky=("N", "S", "E", "W"))
        # self.id_label.pack(side="top", fill="x", expand=True)
        self.output_panel.pack(side="top", fill="both", expand=True)

        self.sv_button.pack(side="left", expand=True)
        self.cc_button.pack(side="right", expand=True)

        self.disable()

    @property
    def name(self):
        return self._name.get()[5:]

    @name.setter
    def name(self, new):
        self._name.set("Name: {}".format(new))

    @property
    def id(self):
        return self._id.get()[11:]

    @id.setter
    def id(self, new):
        self._id.set("Student ID: {}".format(new))

    def disable(self):
        self.name = ""
        self.id = ""
        self.sv_button.configure(state=tk.DISABLED)
        self.cc_button.configure(state=tk.DISABLED)
        self.id_label.configure(state=tk.DISABLED)
        self.nm_label.configure(state=tk.DISABLED)

    def set(self, name, id, success, failure):
        self.name = name
        self.id = id
        self.sv_button.configure(command=success, state=tk.NORMAL)
        self.cc_button.configure(command=failure, state=tk.NORMAL)
        self.id_label.configure(state=tk.NORMAL)
        self.nm_label.configure(state=tk.NORMAL)


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

#
# class ar_Window(tk.Frame):
#     def __init__(self, master, config, **kw):
#         super().__init__(master, **kw)
#         self.pack()
#         self.status_str = tk.StringVar()
#         self.config = config
#         self.image = None
#         self.camera = None
#         self.btn_continue = None
#         self.last_capture = None
#         self.btn_save = None
#         self.label_info = None
#         self.status = tk.Message(self, textvariable=self.status_str)
#
#         self.on_continue = self.hide_result
#         self.on_save = None
#
#         self.status.grid()
#
#     def update_camera(self, cv2_image) -> None:
#         """
#         Call this to update the camera with a cv2 image object
#         :param cv2_image: A cv2 Image
#         :return: None
#         """
#         self.last_capture = cv2_image
#         cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
#         cv2_image = Image.fromarray(cv2_image)
#         self.set_camera(cv2_image)
#
#     def set_camera(self, raw: Image) -> None:
#         """
#         Used internally to update the camera image with an Image Object
#         :param raw: The new PIL image to set the camera to
#         :return: None
#         """
#         if self.camera is None:
#             self.camera = tk.Label(self)
#             self.camera.grid(row=0, column=0)
#         self.camera.raw = raw
#         if self.image is not None:
#             raw = raw.resize(, Image.ANTIALIAS)
#             image = ImageTk.PhotoImage(raw)
#             self.camera.configure(image=image)
#             self.camera.image = image
#
#         def update_prelim(self, result_image) -> None:
#             """
#             Call this function with a cv2 image to update the "result" image
#             Will create a label for the result if one does not exist.
#             :param result_image: A CV2 image object
#             :return: None
#             """
#             raw_img = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
#             raw_img = Image.fromarray(raw_img)
#             if self.image is None:
#                 self.image = tk.Label(self)
#                 self.image.grid(row=0, column=1, rowspan=4)
#                 self.set_camera(self.camera.raw)
#             image = ImageTk.PhotoImage(raw_img)
#
#             self.image.configure(image=image)
#             self.image.raw = image
#
#         def hide_result(self) -> None:
#             """
#             Call this to wipe the current result image from existence and resize the camera
#             :return: None
#             """
#             if self.image is not None:
#                 self.image.grid_forget()
#                 self.image = None
#             if self.btn_continue is not None:
#                 self.btn_continue.grid_forget()
#                 self.btn_continue = None
#             if self.label_info is not None:
#                 self.label_info.grid_forget()
#                 self.label_info = None
#             self.set_camera(self.camera.raw)
#
#         def update_result(self, state, image=None) -> None:
#             """
#             Update Image and card information
#             :param state:
#             :param card: A Card object used to get information about the result
#             :param image: The cv2 image to display
#             :return: None
#             """
#             if image is None:
#                 image = state.frame
#                 card = state.card
#             else:
#                 card = state
#             self.hide_result()
#             self.update_prelim(image)
#             self.btn_continue = tk.Button(self, text="Continue", command=self.on_continue)
#             if self.on_save is not None:
#                 self.btn_save = tk.Button(self, text="Save Record", command=self.on_save)
#                 self.btn_save.grid(row=2, sticky=tk.E + tk.W)
#             student_id = str(card.get_student_id())
#             if card.is_valid():
#                 name = " ".join([str(c) for c in card.get_names()])
#                 label_str = """
# Results:
# Student ID: {student_id}
# Full Name: {name}
#             """.format(student_id=student_id, name=name)
#             else:
#                 label_str = """
#             An error occurred while retrieving the results: {error}
#             """.format(error=str(card.errors))
#             self.label_info = tk.Label(self, text=label_str, justify="left", wraplength=200)
#             self.label_info.card = card
#             self.label_info.grid(row=1, sticky=tk.E + tk.W)
#             self.btn_continue.grid(row=3, sticky=tk.E + tk.W)
