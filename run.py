import argparse
import os
import traceback
from threading import Thread
from tkinter import *

import cv2

import Config
import utilities.io_functions as io
from Card import Card
from functions import output_card_to_image, capture_2
from user_inteface.window import Window
from utilities.Cursor import Cursor


def demo():
    root = Tk()
    w = Window(root, Config)
    camera = cv2.VideoCapture(Config.target_camera)

    def update_camera():
        if camera.isOpened():
            status, img = capture_2(camera)
            w.update_camera(img)
        root.after(10, update_camera)

    def update_capture(event=None):
        image = w.last_capture
        w.update_result(image)

        def complete():
            b = cv2.imencode('.png', image)[1].tostring()
            card = Card.from_image(Config.OutputFormat, b)
            if card is not None:
                revised = output_card_to_image(card, image)
                w.on_result_update(card, revised)

        Thread(target=complete).start()

    def on_save():
        if w.label_info is not None:
            io.insert_record(Config.OutputFormat(), w.label_info.card)
        w.on_continue()

    w.on_save = on_save

    root.bind("<space>", update_capture)

    root.after(10, update_camera)
    root.mainloop()
    camera.release()


def debug(args):
    root = Tk()
    w = Window(root, Config)
    camera = cv2.VideoCapture(Config.target_camera)

    cursor = Cursor(max=len(args))

    def update_camera():
        if camera.isOpened():
            status, img = capture_2(camera)
            w.update_camera(img)
        root.after(5, update_camera)

    def update_capture(event=None):
        image_path, json_path = io.path_from_id(Config.OutputFormat(), args[cursor.index])
        image = cv2.imread(image_path)
        card = Card.from_json_file(Config.OutputFormat(), json_path)

        image = output_card_to_image(card, image)
        w.on_result_update(card, image)

        cursor.increment()

    def on_save():
        pass

    root.bind("<space>", update_capture)

    root.after(1, update_camera)
    root.mainloop()
    camera.release()


def batch(target):
    paths = os.listdir(target)
    images = [path.strip(".temp.png") for path in paths if
              os.path.isfile(target + "/" + path) and path.endswith(".temp.png")]

    root = Tk()
    w = Window(root, Config)

    cursor = Cursor(max=len(images), overflow=False)

    def update_camera():
        if cursor.index == 0:
            id = images[-1]
        else:
            id = images[cursor.index + 1]
        path, _ = io.path_from_id(Config.OutputFormat(), id)
        image = cv2.imread(path)
        w.update_camera(image)
        root.after(250, update_camera)

    def update_capture(event=None):
        path, _ = io.path_from_id(Config.OutputFormat(), images[cursor.index])
        image = cv2.imread(path)
        w.update_result(image)

        def complete():
            b = cv2.imencode('.png', image)[1].tostring()
            card = Card.from_image(Config.OutputFormat, b)
            if card is not None:
                revised = output_card_to_image(card, image)
                w.on_result_update(card, revised)

        cursor.increment()
        Thread(target=complete).start()

    def save():
        if w.label_info is not None:
            io.insert_record(Config.OutputFormat(), w.label_info.card)

    w.on_save = save

    root.bind("<space>", update_capture)

    root.after(1, update_camera)
    root.after(10, update_capture)
    root.mainloop()


parser = argparse.ArgumentParser(description='Process RMIT student cards and output their attributes to a CSV file.')
mode = parser.add_mutually_exclusive_group(required=False)
mode.add_argument('-b', '--batch', help="Parse all images in the directory given")
mode.add_argument('-d', '--debug', nargs=argparse.REMAINDER, help="Run the listed images in replay/debug mode")

files = parser.parse_args()

if files.debug:
    debug(files.debug)
elif files.batch:
    batch(files.batch)
else:
    try:
        demo()
    except BaseException as ignored:
        traceback.print_exc()
