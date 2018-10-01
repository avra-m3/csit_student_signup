import tkinter as tk

from functions import cv_2_pil
from user_inteface.CameraPane import CameraPane
from user_inteface.ErrorDialog import ErrorDialog
from user_inteface.OutputPane import OutputPane
from user_inteface.RecordPanel import RecordPanel


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

        self.record.set((card.firstname, card.lastname), card.student_id, success, cancel)
        self.output.update_image(image)

    def reset(self):
        self.output.reset()
        self.record.disable()
