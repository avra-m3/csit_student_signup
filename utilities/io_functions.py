import csv
import os
import shutil
import time
from typing import Tuple

import cv2
from requests import Response

from utilities.templates import OutputObject


def validate_entry(entry: dict, config: OutputObject) -> bool:
    """
    Validates an entry to ensure it does not exist if config.enforce_unique is True
    :param entry: A dictionary mapping columns to rows, the entry to be validated
    :param config: An OutputFormat object
    :return: boolean, does this entry already exist
    """
    if not config.enforce_unique:
        return True
    if not os.path.isfile(config.file):
        return True
    with open(config.file, "r", newline="") as raw_in:
        file = csv.DictReader(raw_in, fieldnames=config.columns, dialect=csv.excel)
        for row in file:
            if entry[config.primary_key] == row[config.primary_key]:
                return False
    return True


def insert_row(config, name, sid, insert_time) -> bool:
    row = [
        entry.format(
            student_id=sid,
            name=name,
            date=insert_time
        ) for entry in config.rows
    ]
    entry = dict(zip(config.columns, row))
    if validate_entry(entry, config):
        with open(config.file, "a") as output:
            file = csv.DictWriter(output, fieldnames=config.columns, dialect=csv.excel)
            print(entry)
            file.writerow(entry)
        return True
    return False


def insert_record(config, card, override_time=None) -> bool:
    """
    Insert a record into the output file defined in config
    :param override_time: override the insert time with a string object
    :param card: The card to write
    :param config: The configuration, an OutputFormat object
    :return: None
    """
    if not os.path.isfile(config.file):
        create_csv(config)

    now = time.localtime()
    return insert_row(config, card.get_name(), card.get_student_id(), override_time or now)


def create_csv(config: OutputObject) -> None:
    """Backup file if it already exists, then create a new csv file"""
    if os.path.exists(config.file):
        new_path = "{cache}/output_{date}.backup.csv".format(cache=config.cache_dir,
                                                             date=time.strftime("%Y%m%d%H%M%S", time.localtime()))
        shutil.copyfile(config.file, new_path)
    with open(config.file, "w+") as output:
        file = csv.DictWriter(f=output, fieldnames=config.columns, dialect=csv.excel)
        file.writeheader()


def create_backup_dir(config: OutputObject) -> None:
    """ Create the Image Backup directory if it does not exist
        Can throw an IO exception if the path already exists as a non-dir
    """
    if not os.path.exists(config.cache_dir):
        os.mkdir(config.cache_dir)


def init(config) -> None:
    """
    This function calls create_csv and create_backup_dir
    :param config: An OutputFormat object
    :return: None
    """
    create_backup_dir(config)
    # create_csv(config)


def cache_image(image, config: OutputObject) -> str:
    """
    Writes a copy of an image to disk
    :param image: The cv2 image object
    :param config: The Output Object configurations
    :return: path where image was saved
    """
    now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    path, _ = path_from_id(config, now)
    i = 0
    while os.path.isfile(path):
        path, _ = path_from_id(config, "{time}-{index}").format(time=now, index=i)
        i += 1
    cv2.imwrite(path, image)
    return path


def path_from_id(config: OutputObject, id: str) -> Tuple[str, str]:
    image = "{cache}/{id}.temp.png".format(cache=config.cache_dir, id=id)
    json = "{cache}/{id}.json".format(cache=config.cache_dir, id=id)
    return image, json


def cache_response(response: Response, path: str, config: OutputObject):
    image_id = path.strip(".temp.png").split("/")[-1]
    _, path = path_from_id(config, image_id)
    with open(path, "wb") as output:
        output.write(response.content)


def cache(config: OutputObject, response: Response, image: bytes):
    now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    i_path, json = path_from_id(config, now)
    i = 0
    while os.path.isfile(i_path) or os.path.isfile(json):
        i_path, json = path_from_id(config, "{time}-{index}").format(time=now, index=i)
        i += 1

    with open(json, "wb") as output:
        output.write(response.content)
    with open(i_path, "wb") as output:
        output.write(image)


__all__ = [init, insert_record, cache_image]
