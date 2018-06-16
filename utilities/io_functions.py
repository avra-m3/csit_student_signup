import csv
import shutil
import time
import os


def validate_entry(entry: dict, config) -> bool:
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
        file = csv.DictReader(raw_in, fieldnames=config.columns, dialect=csv.get_dialect(csv.excel))
        for row in file:
            if entry[config.primary_key] == row[config.primary_key]:
                return False
    return True


def insert_record(card, config) -> None:
    if not os.path.isfile(config.file):
        create_csv(config)

    now = time.localtime()
    row = [
        entry.format(
            student_id=card.get_student_id(),
            name=card.name_as_str(),
            date=time.strftime("%Y/%m/%d %H:%M", now)
        ) for entry in config.rows
    ]
    entry = dict(zip(config.columns, row))
    if validate_entry(entry,config):
        with open(config.file, "a") as output:
            file = csv.DictWriter(f=output, fieldnames=config.columns, dialect=csv.get_dialect(csv.excel))
            file.writerow(entry)


def create_csv(config) -> None:
    """Backup file if it already exists, then create a new csv file"""
    if os.path.exists(config.file):
        new_path = "{path}.{date}_backup.csv".format(path=config.file,
                                                     date=time.strftime("%Y%m%d%H%M%S", time.localtime()))
        shutil.copyfile(config.file, new_path)
    with open(config.file, "w+") as output:
        file = csv.DictWriter(f=output, fieldnames=config.columns, dialect=csv.get_dialect(csv.excel))
        file.writeheader()


def create_backup_dir(config) -> None:
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
    create_csv(config)
    create_backup_dir(config)


__all__ = [init, insert_record, create_csv]
