import datetime

import cv2

import Config
from Card import Card
from functions import output_card_to_image
from ocr_detection import barcode


class STATES:
    MONITOR = "monitoring"
    DETECT = "detected"
    CAPTURE = "processing"
    ERRORED = "errored"
    SUCCESS = "success"


class State:
    def __init__(self, camera):
        self.camera = camera
        self._status = "starting"
        self.last_state_change = None

        self.frame = None
        self.debug_frame = None
        self.result_frame = None

        self.card = None
        self.snap()
        print(camera.isOpened())
        print(camera.read())

    @property
    def image(self):
        if self.frame is None:
            return None
        return cv2.imencode('.png', self.frame)[1].tostring()

    @property
    def im_debug(self):
        if self.debug_frame is None:
            return None
        return cv2.imencode('.png', self.debug_frame)[1].tostring()

    @property
    def im_result(self):
        if self.result_frame is None:
            return None
        return cv2.imencode('.png', self.result_frame)[1].tostring()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status == self._status:
            return
        self.last_state_change = datetime.datetime.now()
        self._status = status

    @property
    def modified(self):
        return self.last_state_change

    def snap(self):
        status = None
        if self.camera.isOpened:
            status, self.frame = self.camera.read()
        if not status:
            self.frame = None
            self.status = STATES.ERRORED

    def dim_frame(self):
        if self.frame is not None:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def find_barcode(self):
        if self != STATES.ERRORED:
            self.debug_frame, success, bounds = barcode.detect(self.frame)
            if success > -1:
                self.status = STATES.DETECT
            else:
                self.status = STATES.MONITOR

    def get_card(self):
        self.result_frame = None
        self.card = Card.from_image(Config.OutputFormat, self.image)
        if self.card is not None:
            self.result_frame = output_card_to_image(self.card, self.frame)
            self.status = STATES.SUCCESS
        else:
            self.reset_lifecycle()

    def reset_lifecycle(self):
        self.status = STATES.MONITOR

    def __eq__(self, other):
        if isinstance(other, str):
            return self.status == other
        else:
            return False

    def __str__(self):
        return self.status[0].upper() + self.status[1:]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.camera.release()
        pass
