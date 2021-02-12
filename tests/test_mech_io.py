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
        test_filepath = gen_csvpath("test", Path(__file__).parent, "2000-01-01")
        write_csv(test_data, test_filepath, ['test_col'])

        with open(test_filepath, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual("test value", result_data[0]['test_col'])
        os.remove(test_filepath)
