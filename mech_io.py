import sqlite3
from pathlib import Path
import os
import csv
import datetime
import json


def write_csv(data, filepath, fields, overwrite=False):
    # TODO: implement a check if this file exists already, use overwrite param to control if it overwrites
    if type(data) not in [list, dict]:
        raise ValueError("input should be a list or a list of dicts to write")

    with open(filepath, 'w', encoding="utf-8", newline='') as out_csv:
        out_writer = csv.DictWriter(out_csv, fieldnames=fields)
        out_writer.writeheader()
        if type(data) == dict:
            out_writer.writerow(data)
        else:
            out_writer.writerows(data)

    return


def append_csv(data, filepath, fields, overwrite=False):
    # TODO: implement a check if this file exists already, use overwrite param to control if it overwrites
    if type(data) not in [list, dict]:
        raise ValueError("input should be a list or a list of dicts to write")

    with open(filepath, 'a', encoding="utf-8", newline='') as out_csv:
        out_writer = csv.DictWriter(out_csv, fieldnames=fields)
        if type(data) == dict:
            out_writer.writerow(data)
        else:
            out_writer.writerows(data)

    return


def prepare_appending_csv(filepath, fields):
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding="utf-8", newline='') as prep_csv:
            prep_reader = csv.DictReader(prep_csv)
            if prep_reader.fieldnames != fields:
                raise ValueError("unexpected fields found in file at filepath")
            return True
    else:
        with open(filepath, 'w', encoding="utf-8", newline='') as prep_csv:
            prep_writer = csv.DictWriter(prep_csv, fieldnames=fields)
            prep_writer.writeheader()
        return True


def read_csv(filepath):
    with open(filepath, 'r', encoding="utf-8", newline='') as in_csv:
        in_reader = csv.DictReader(in_csv)
        read_data = [csv_row for csv_row in in_reader]

    return read_data


def gen_csvpath(suffix, folder=None, date=None):
    if not folder:
        folder = Path(__file__).parent / "data"
    if not date:
        date = datetime.date.today().isoformat()

    filename = date + "_" + suffix + ".csv"

    return folder / filename


def write_post_json(topic_id, data, folder=None):
    if not folder:
        folder = Path(__file__).parent / "data" / "post_data"

    filename = "topic" + topic_id + "_postdata.json"
    json_filepath = folder / filename

    json_data = json.dumps(data, indent=4, default=(lambda x: x.__str__()))
    with open(json_filepath, 'w') as json_file:
        json_file.write(json_data)

    return
