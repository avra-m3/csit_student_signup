import time

import os

import Card
import Config


class FileHandler:
    def __init__(self, cache_dir: str, output_file_path: str):
        if not os.path.exists(output_file_path):
            self.record = open(output_file_path, "w")
            self.record.write("snumber,name,email,time\n")
        elif os.path.isfile(Config.output_file):
            self.record = open(output_file_path, 'a+')
        else:
            raise IOError()

        # for image save handling
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)

    def save_to_cache(self, file: str, ext: str) -> str:
        file_path = Config.cache_dir + '/temp_' + str(time.time()) + ext
        with open(file_path, 'w+') as temp_file:
            temp_file.write(file)
        return file_path

    def save_to_record(self, card: Card) -> None:
        now = time.localtime()
        snumber = card.get_student_id()
        name = card.name_as_str()
        self.record.write(
            "s%s,%s,s%s@student.rmit.edu.au,%s\n" % (snumber, name, snumber, "%.4d/%.2d/%.2d %.2d:%.2d" % (
                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)))
        self.record.flush()

    def __del__(self):
        self.record.close()
