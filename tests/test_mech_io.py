import os
from mech_io import *
from unittest import TestCase


class TestGenCsvpath(TestCase):
    def test_gen_csvpath(self):
        test_filename = "2000-01-01_test.csv"
        test_path = Path(__file__) / test_filename
        self.assertEqual(test_path, gen_csvpath("test", Path(__file__), "2000-01-01"))

        test_default_filename = datetime.date.today().isoformat() + "_test.csv"
        test_default_path = Path(__file__).parent.parent / "data" / test_default_filename
        self.assertEqual(test_default_path, gen_csvpath("test"))


class TestWriteCsv(TestCase):
    def test_write_csv(self):
        test_data = [{'test_col': "test value"}]
        test_filepath = Path(__file__).parent / "fixtures" / "test_write.csv"
        write_csv(test_data, test_filepath, ['test_col'])

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual("test value", result_data[0]['test_col'])
        os.remove(test_filepath)

    def test_write_csv_single(self):
        test_data = {'test_col': "test value"}
        test_filepath = Path(__file__).parent / "fixtures" / "test_write.csv"
        write_csv(test_data, test_filepath, ['test_col'])

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual("test value", result_data[0]['test_col'])
        os.remove(test_filepath)

    def test_write_csv_valueerror(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_write.csv"

        with self.assertRaises(ValueError):
            write_csv(123, test_filepath, ['test_col'])
            os.remove(test_filepath)


class TestAppendCsv(TestCase):
    def test_append_csv(self):
        test_data = [{'test_col': "appended value"}]
        test_filepath = Path(__file__).parent / "fixtures" / "test_append.csv"
        with open(test_filepath, 'w', encoding="utf-8", newline='') as test_csv:
            test_writer = csv.DictWriter(test_csv, fieldnames=['test_col'])
            test_writer.writeheader()
            test_writer.writerow({'test_col': "initial value"})

        append_csv(test_data, test_filepath, ['test_col'])

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual("initial value", result_data[0]['test_col'])
        self.assertEqual("appended value", result_data[1]['test_col'])
        os.remove(test_filepath)

    def test_append_csv_single(self):
        test_data = {'test_col': "appended value"}
        test_filepath = Path(__file__).parent / "fixtures" / "test_append.csv"
        with open(test_filepath, 'w', encoding="utf-8", newline='') as test_csv:
            test_writer = csv.DictWriter(test_csv, fieldnames=['test_col'])
            test_writer.writeheader()
            test_writer.writerow({'test_col': "initial value"})

        append_csv(test_data, test_filepath, ['test_col'])

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual("initial value", result_data[0]['test_col'])
        self.assertEqual("appended value", result_data[1]['test_col'])
        os.remove(test_filepath)

    def test_append_csv_valueerror(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_append.csv"

        with self.assertRaises(ValueError):
            append_csv(123, test_filepath, ['test_col'])
            os.remove(test_filepath)


class TestPrepareCsv(TestCase):
    def test_prepare_appending_csv_existing(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_csv.csv"
        self.assertTrue(prepare_appending_csv(test_filepath, ['test_col1', 'test_col2']))
        with self.assertRaises(ValueError):
            prepare_appending_csv(test_filepath, ['not_field', 'test_col2'])

    def test_prepare_appending_csv_new(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_prepare.csv"
        test_fields = ['test_col1', 'test_col2']
        prepare_appending_csv(test_filepath, test_fields)

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_fields = result_reader.fieldnames

        self.assertEqual(test_fields, result_fields)
        os.remove(test_filepath)


class TestReadCsv(TestCase):
    def test_read_csv(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_csv.csv"
        test_data = read_csv(test_filepath)

        self.assertEqual(3, len(test_data))
        self.assertEqual("col1_0", test_data[0]['test_col1'])
        self.assertEqual("col2_1", test_data[1]['test_col2'])


class TestWritePostJson(TestCase):
    def test_write_post_json(self):
        test_folder = Path(__file__).parent / "fixtures"
        test_filepath = test_folder / "topic_test_postdata.json"
        test_data = {"test_col1": "test_val", "test_col2": ["test_val1", "test_val2"]}

        write_post_json("_test", test_data, test_folder)

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_json:
            result_data = json.load(result_json)

        self.assertEqual(test_data, result_data)
        os.remove(test_filepath)


class TestDBSetup(TestCase):
    def test_db_setup(self):
        # TODO: improve test_db_setup() to actually test the name/schema of the created dbs
        test_setup = Path(__file__).parent / "fixtures" / "test_setup.db"
        db_setup(test_setup)

        conn = sqlite3.connect(test_setup)
        tables = conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'""")
        table_list = tables.fetchall()
        self.assertEqual(6, len(table_list))
        conn.close()
        os.remove(test_setup)


class TestDBInsertBoardRaw(TestCase):
    def setUp(self):
        self.test_db = Path(__file__).parent / "fixtures" / "test_insert.db"
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE board_raw (
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
                    """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.remove(self.test_db)

    def test_db_insert_board_raw(self):
        # TODO: redo this unit test to not rely on constantly remaking db/figure out how to actually delete if crash

        conn = sqlite3.connect(self.test_db)
        conn.row_factory = sqlite3.Row
        test_data = [{'topic_link': "test_insert1", 'creator': "test_insert2", 'creator_link': None, 'views': None,
                      'replies': None, 'last_post': None, 'url': None, 'accessed': None, 'title': None},
                     {'topic_link': "test_insert3", 'creator': None, 'creator_link': None, 'views': None,
                      'replies': None, 'last_post': None, 'url': None, 'accessed': None, 'title': None}
                     ]
        db_insert_board_raw(test_data, db=self.test_db)

        result_data = conn.execute("""SELECT * FROM board_raw""").fetchall()
        conn.close()
        self.assertEqual("test_insert1", result_data[0]['topic_link'])
        self.assertEqual("test_insert2", result_data[0]['creator'])
        self.assertEqual("test_insert3", result_data[1]['topic_link'])

    def test_db_insert_board_raw_single(self):
        conn = sqlite3.connect(self.test_db)
        conn.row_factory = sqlite3.Row
        test_data = {'topic_link': "test_insert1", 'creator': "test_insert2", 'creator_link': None, 'views': None,
                     'replies': None, 'last_post': None, 'url': None, 'accessed': None, 'title': None}
        db_insert_board_raw(test_data, db=self.test_db)

        result_data = conn.execute("""SELECT * FROM board_raw""").fetchall()
        conn.close()
        self.assertEqual("test_insert1", result_data[0]['topic_link'])
        self.assertEqual("test_insert2", result_data[0]['creator'])

    def test_db_insert_board_raw_error(self):
        with self.assertRaises(ValueError):
            db_insert_board_raw("improper input", db=self.test_db)
