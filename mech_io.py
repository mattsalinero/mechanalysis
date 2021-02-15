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


def db_setup(db, overwrite=False):
    # TODO: implement unit test for this
    if os.path.isfile(db):
        if overwrite:
            os.remove(db)
        else:
            raise FileExistsError("db file already exists")

    table_sqls = {}
    table_sqls['topic_data'] = """CREATE TABLE topic_data (
        topic_id VARCHAR PRIMARY KEY,
        topic_created VARCHAR,
        product_type VARCHAR,
        thread_type VARCHAR,
        set_name VARCHAR,
        creator VARCHAR,
        creator_id VARCHAR,      
        views INTEGER,
        replies INTEGER,
        board VARCHAR,
        topic_accessed VARCHAR,
        board_accessed VARCHAR,
        title VARCHAR); 
        """
    table_sqls['topic_icode'] = """CREATE TABLE topic_icode (
        topic_id VARCHAR NOT NULL,
        info_code VARCHAR NOT NULL,
        PRIMARY KEY (topic_id, info_code),
        FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id));
        """
    # table_sqls['topic_link'] = """CREATE TABLE page_link (
    #     id INTEGER PRIMARY KEY,
    #     topic_id VARCHAR NOT NULL,
    #     link VARCHAR NOT NULL);
    #     """
    # table_sqls['topic_image'] = """CREATE TABLE page_image (
    #     id INTEGER PRIMARY KEY,
    #     topic_id VARCHAR NOT NULL,
    #     image_source VARCHAR NOT NULL);
    #     """

    conn = sqlite3.connect(db)
    c = conn.cursor()

    for table in table_sqls.keys():
        c.execute(table_sqls[table])
    conn.commit()
    conn.close()

    return


def _db_check_exists(db, setup=False):
    # TODO: unit test?
    if os.path.exists(db):
        return True
    elif setup:
        db_setup(db)
        return False
    else:
        raise FileNotFoundError("db file does not exist")


def db_insert_board_clean(data, db=None, new_db=True):
    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db"

    _db_check_exists(db, setup=new_db)

    if type(data) == dict:
        values = [data]
    elif type(data) == list:
        values = data
    else:
        raise ValueError("data should be dict or list of dicts with keys corresponding to table schema")

    info_codes = []
    for entry in values:
        if entry['info_codes']:
            for info_code in entry['info_codes']:
                info_codes.append({'topic_id': entry['topic_id'], 'info_code': info_code})

    topic_data_query = """INSERT INTO topic_data (topic_id, product_type, thread_type, set_name, creator, creator_id, 
                                        views, replies, board, board_accessed, title)
                VALUES (:topic_id, :product_type, :thread_type, :set_name, :creator, :creator_id, :views,
                  :replies, :board, :access_date, :title);
                """
    topic_icode_query = """INSERT OR REPLACE INTO topic_icode (topic_id, info_code)
                VALUES (:topic_id, :info_code);
                """

    conn = sqlite3.connect(db)

    conn.executemany(topic_data_query, values)
    conn.executemany(topic_icode_query, info_codes)

    conn.commit()
    conn.close()

    return


def db_insert_topic_clean(data, db=None):
    # TODO: fix "accessed" vs "topic_accessed" in schema
    # TODO: implement unit test

    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db"

    _db_check_exists(db, setup=False)

    if type(data) == dict:
        values = [data]
    elif type(data) == list:
        values = data
    else:
        raise ValueError("data should be dict or list of dicts with keys corresponding to table schema")

    topic_data_query = """
        UPDATE topic_data
        SET topic_created = :topic_created,
            topic_accessed = :accessed
        WHERE topic_id = :topic_id;"""

    conn = sqlite3.connect(db)

    conn.executemany(topic_data_query, values)

    conn.commit()
    conn.close()

    return


def db_query_keycap_topics(db=None, board=None, select_restriction=None):
    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db"

    values = {}
    board_condition = ""
    if board:
        board_condition = "AND board = :board"
        values['board'] = board

    extra_condition = ""
    if select_restriction:
        if select_restriction == "new":
            extra_condition = "AND topic_accessed IS NULL"
        else:
            raise ValueError("available select types are None and 'new'")

    keycap_topic_query = f"""SELECT topic_id
                          FROM topic_data
                          WHERE product_type = 'keycaps' {board_condition} {extra_condition};
                          """

    conn = sqlite3.connect(db)

    keycap_topic_list = [entry[0] for entry in conn.execute(keycap_topic_query, values).fetchall()]

    conn.commit()
    conn.close()

    return keycap_topic_list
