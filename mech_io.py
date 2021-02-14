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


def db_setup(db):
    # TODO: implement check/logic if the db already exists - otherwise could mess up the structure (and will throw
    #  error if a table already exists)

    conn = sqlite3.connect(db)
    c = conn.cursor()

    table_sqls = {}
    table_sqls['board_raw'] = """CREATE TABLE board_raw (
        id INTEGER PRIMARY KEY,
        title VARCHAR,
        topic_link VARCHAR NOT NULL,
        creator VARCHAR,
        creator_link VARCHAR,
        views VARCHAR,
        replies VARCHAR,
        last_post VARCHAR,
        url VARCHAR,
        accessed VARCHAR); 
        """
    table_sqls['page_raw'] = """CREATE TABLE page_raw (
        topic_id INTEGER PRIMARY KEY,
        topic_created VARCHAR,
        topic_accessed VARCHAR);
        """
    table_sqls['page_link'] = """CREATE TABLE page_link (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        link VARCHAR NOT NULL);
        """
    table_sqls['page_image'] = """CREATE TABLE page_image (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        image_source VARCHAR NOT NULL);
        """
    table_sqls['topic_data'] = """CREATE TABLE topic_data (
        topic_id INTEGER PRIMARY KEY,
        product_type VARCHAR,
        thread_type VARCHAR,
        set_name VARCHAR,
        creator VARCHAR,
        creator_id INTEGER,      
        views INTEGER,
        replies INTEGER,
        board INTEGER,
        board_accessed VARCHAR
        title VARCHAR); 
        """
    table_sqls['topic_icode'] = """CREATE TABLE topic_icode (
        topic_id INTEGER NOT NULL,
        info_code VARCHAR NOT NULL,
        PRIMARY KEY (topic_id, info_code));
        """

    for table in table_sqls.keys():
        c.execute(table_sqls[table])
    conn.commit()
    conn.close()
    return


def db_insert_board_raw(data, db=None):
    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db"

    if type(data) == dict:
        values = [data]
    elif type(data) == list:
        values = data
    else:
        raise ValueError("data should be dict or list of dicts with keys corresponding to table schema")

    conn = sqlite3.connect(db)

    query = """INSERT INTO board_raw (title, topic_link, creator, creator_link, 
                                        views, replies, last_post, url, accessed)
                VALUES (:title, :topic_link, :creator, :creator_link, :views, :replies, :last_post, :url, :accessed);
                """

    conn.executemany(query, values)
    conn.commit()
    conn.close()

    return
