import sqlite3
from pathlib import Path
import os
import csv
import datetime
import json


def write_csv(data, filepath, fields, overwrite=False):
    """
    Writes given dict of data to .csv
    :param data: dict of data
    :param filepath: filepath to save to
    :param fields: list giving schema of data
    :param overwrite:
    :return: none
    """
    # TODO: implement a check if this file exists already, use overwrite param to control if it overwrites
    # TODO: replace fields with param data.keys() because they should be equivalent now (and less maintenance)
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
    """
    Appends given dict of data to .csv
    :param data: dict of data
    :param filepath: filepath to save to
    :param fields: list of fieldnames giving schema of data
    :param overwrite:
    :return: none
    """
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
    """
    Verifies file to append to is correctly formatted (or creates file)
    :param filepath: filepath of file to check
    :param fields: list of fieldnames giving schema of data
    :return: True if successful (mostly redundant)
    """
    if os.path.isfile(filepath):
        # checks if already existing file has the correct format
        with open(filepath, 'r', encoding="utf-8", newline='') as prep_csv:
            prep_reader = csv.DictReader(prep_csv)
            if prep_reader.fieldnames != fields:
                raise ValueError("unexpected fields found in file at filepath")
            return True
    else:
        # sets up new file
        with open(filepath, 'w', encoding="utf-8", newline='') as prep_csv:
            prep_writer = csv.DictWriter(prep_csv, fieldnames=fields)
            prep_writer.writeheader()
        return True


def read_csv(filepath):
    """
    Reads .csv at filepath to list of dicts
    :param filepath: filepath of file to read
    :return: list[dict] of data in .csv
    """
    with open(filepath, 'r', encoding="utf-8", newline='') as in_csv:
        in_reader = csv.DictReader(in_csv)
        read_data = [csv_row for csv_row in in_reader]

    return read_data


def gen_csvpath(suffix, folder=None, date=None):
    """
    Generates appropriate filename/path for .csv based on date
    :param suffix: suffix of filename in addition to date
    :param folder: Path object to folder of tile
    :param date: date (default is today's date)
    :return: Path object to file
    """
    if not folder:
        folder = Path(__file__).parent / "data"
    if not date:
        date = datetime.date.today().isoformat()

    filename = date + "_" + suffix + ".csv"

    return folder / filename


def write_post_json(topic_id, data, folder=None):
    """
    Writes given data to individual .json file
    :param topic_id: topic_id of data (for filename generation)
    :param data: dict of data to write
    :param folder: path to folder .json will be saved
    :return: none
    """
    if not folder:
        folder = Path(__file__).parent / "data" / "post_data"
    filename = "topic" + topic_id + "_post_data.json"
    json_filepath = folder / filename

    json_data = json.dumps(data, indent=4, default=(lambda x: x.__str__()))
    with open(json_filepath, 'w') as json_file:
        json_file.write(json_data)

    return


def read_post_json(topic_id=None, folder=None, filepath=None):
    """
    Reads individual post data from .json file based on topic_id
    :param topic_id: topic_id of data (for filename generation)
    :param folder: path to folder .json will be saved
    :param filepath: full filepath (priority over generated filepath)
    :return: dict of data from .json
    """
    if filepath:
        json_filepath = filepath
    elif topic_id:
        if not folder:
            folder = Path(__file__).parent / "data" / "post_data"
        filename = "topic" + topic_id + "_post_data.json"
        json_filepath = folder / filename
    else:
        raise ValueError("no file specified")

    with open(json_filepath, 'r') as json_file:
        json_data = json.load(json_file)

    return json_data


def db_setup(db, overwrite=False):
    """
    Sets up SQLite database based on given schema
    :param db: filepath to desired location of database
    :param overwrite:
    :return: none
    """
    # TODO: implement unit test for this
    if os.path.isfile(db):
        if overwrite:
            os.remove(db)
        else:
            raise FileExistsError("db file already exists")

    table_sqls = {}
    table_sqls['topic_data'] = """
        CREATE TABLE topic_data (
        topic_id VARCHAR PRIMARY KEY,
        product_type VARCHAR,
        thread_type VARCHAR,
        set_name VARCHAR,
        creator VARCHAR,
        creator_id VARCHAR,      
        views INTEGER,
        replies INTEGER,
        board VARCHAR,
        board_accessed VARCHAR,
        title VARCHAR); 
        """
    table_sqls['topic_icode'] = """
        CREATE TABLE topic_icode (
        topic_id VARCHAR NOT NULL,
        info_code VARCHAR NOT NULL,
        PRIMARY KEY (topic_id, info_code),
        FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id));
        """
    table_sqls['topic_advanced'] = """
        CREATE TABLE topic_advanced (
        topic_id VARCHAR PRIMARY KEY,
        topic_created VARCHAR,
        num_posts INTEGER,
        num_posters INTEGER,
        num_creator_posts INTEGER,
        percent_creator_posts FLOAT,
        post_25_delta VARCHAR,
        post_50_delta VARCHAR,
        topic_accessed VARCHAR,
        FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id));
        """
    table_sqls['topic_link'] = """
        CREATE TABLE topic_link (
        id INTEGER PRIMARY KEY,
        topic_id VARCHAR NOT NULL,
        link VARCHAR NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id));
        """

    conn = sqlite3.connect(db)
    c = conn.cursor()

    for table in table_sqls.keys():
        c.execute(table_sqls[table])
    conn.commit()
    conn.close()

    return


def _db_check_exists(db, setup=False):
    # checks if given database exists
    # TODO: unit test?
    if os.path.exists(db):
        return True
    elif setup:
        db_setup(db)
        return False
    else:
        raise FileNotFoundError("db file does not exist")


def db_insert_board_clean(data, db=None, new_db=True):
    """
    Inserts given board data into database
    :param data: list[dict] or [dict] of data to insert
    :param db: path to database
    :param new_db: is this going into a new database?
    :return: none
    """
    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db.db"

    _db_check_exists(db, setup=new_db)

    if type(data) == dict:
        values = [data]
    elif type(data) == list and type(data[0]) == dict:
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
                  :replies, :board, :board_accessed, :title);
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
    """
    Inserts topic data into database
    :param data: list[dict] or [dict] of data to insert
    :param db: path to database
    :return: none
    """
    # TODO: implement unit test and expand to include new statistics

    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db.db"

    _db_check_exists(db, setup=False)

    if type(data) == dict:
        values = [data]
    elif type(data) == list and type(data[0]) == dict:
        values = data
    else:
        raise ValueError("data should be dict or list of dicts with keys corresponding to table schema")

    post_links = []
    for entry in values:
        if entry['post_links']:
            for link in entry['post_links']:
                post_links.append({'topic_id': entry['topic_id'], 'link': link})

    topic_advanced_query = """
        INSERT INTO topic_advanced (topic_id, topic_created, num_posts, num_posters, num_creator_posts,
            percent_creator_posts, post_25_delta, post_50_delta, topic_accessed) 
        VALUES (:topic_id, :topic_created, :num_posts, :num_posters, :num_creator_posts,
            :percent_creator_posts, :post_25_delta, :post_50_delta, :topic_accessed);
        """

    topic_link_query = """INSERT OR REPLACE INTO topic_link (topic_id, link)
                VALUES (:topic_id, :link);
                """

    conn = sqlite3.connect(db)

    conn.executemany(topic_advanced_query, values)
    conn.executemany(topic_link_query, post_links)

    conn.commit()
    conn.close()

    return


def db_query_keycap_topics(db=None, board=None, select_restriction=None):
    """
    Searches database to determine list of keycap topics
    :param db: path to database
    :param board: (optional) board to restrict search
    :param select_restriction: (optional) "new" if only want new topics
    :return: list of relevant topic_ids
    """
    # TODO: rename select_restriction to something more descriptive
    if not db:
        db = Path(__file__).parent / "data" / "database" / "mech_db.db"

    values = {}
    board_condition = ""
    if board:
        board_condition = "AND topic_data.board = :board"
        values['board'] = board

    extra_condition = ""
    if select_restriction:
        if select_restriction == "new":
            extra_condition = "AND topic_advanced.topic_accessed IS NULL"
        else:
            raise ValueError("available select types are None and 'new'")

    keycap_topic_query = f"""SELECT topic_data.topic_id
                          FROM topic_data LEFT JOIN topic_advanced
                            ON topic_data.topic_id = topic_advanced.topic_id
                          WHERE topic_data.product_type = 'keycaps' {board_condition} {extra_condition};
                          """

    conn = sqlite3.connect(db)

    keycap_topic_list = [entry[0] for entry in conn.execute(keycap_topic_query, values).fetchall()]

    conn.commit()
    conn.close()

    return keycap_topic_list


def db_query(query, db=None, existing_conn=None):
    """
    Executes query
    :param query: string of SQL query to execute
    :param db: optional path to SQLite db to query
    :param existing_conn: optional existing connection to a db
    :return: query results
    """
    # TODO: add unit test for this
    # TODO: implement a check that this is a select statement only
    if existing_conn:
        conn = existing_conn
    elif db:
        conn = sqlite3.connect(db)
    else:
        raise ValueError("need value for one of db and existing_conn")

    query_result = conn.execute(query).fetchall()

    conn.commit()

    if not existing_conn:
        conn.close()

    return query_result
