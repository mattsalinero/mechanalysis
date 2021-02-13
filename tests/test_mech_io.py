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
