import sqlite3
from pathlib import Path
import csv
import datetime
import json


def write_csv(data, filepath, fields, mode='w', overwrite=False):
    # TODO: implement a check if this file exists already, use overwrite param to control if it overwrites
    with open(filepath, mode, encoding="utf-8", newline='') as out_csv:
        out_writer = csv.DictWriter(out_csv, fieldnames=fields)
        out_writer.writeheader()
        out_writer.writerows(data)


def gen_csvpath(suffix, folder=None, date=None):
    if not folder:
        folder = Path(__file__).parent / "data"
    if not date:
        date = datetime.date.today().isoformat()

    filename = date + "_" + suffix + ".csv"

    return folder / filename
