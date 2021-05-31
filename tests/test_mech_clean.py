import datetime
import os
import sqlite3

from mech_clean import *
from unittest import TestCase


class TestParseBasic(TestCase):
    def test_parse_basic_topic_id(self):
        testinput = {'topic_link': "https://testsite.org/index.php?topic=123456.0"}
        self.assertEqual(parse_basic(testinput)['topic_id'], "123456")

    def test_parse_basic_bad_topic_id(self):
        blankinput = {'topic_link': None, 'creator': None, 'creator_link': None, 'views': None, 'replies': None,
                      'last_post': None, 'url': None, 'board_accessed': None, 'title': None}
        with self.assertRaises(ValueError):
            parse_basic(blankinput)
        with self.assertRaises(ValueError):
            parse_basic({})

    def test_parse_basic_proper_input(self):
        testinput = {'title': "test title",
                     'topic_link': "https://testsite.org/index.php?topic=123456.0",
                     'creator': "test creator",
                     'creator_link': "https://testsite.org/index.php?action=profile;u=123456",
                     'replies': "123 Replies",
                     'views': "456 Views",
                     'last_post': datetime.datetime.fromisoformat("2001-01-01 01:01:01"),
                     'url': "https://geekhack.org/index.php?board=70.0;sort=first_post;desc",
                     'board_accessed': datetime.datetime.fromisoformat("2002-02-02 02:02:02")
                     }

        testoutput = parse_basic(testinput)

        self.assertEqual(testoutput['creator'], "test creator")
        self.assertEqual(testoutput['creator_id'], "123456")
        self.assertEqual(testoutput['views'], 456)
        self.assertEqual(testoutput['replies'], 123)
        self.assertEqual(testoutput['board_id'], "70")
        self.assertEqual(testoutput['board_accessed'], datetime.datetime.fromisoformat("2002-02-02 02:02:02"))
        self.assertEqual(testoutput['title'], "test title")

    def test_parse_basic_blank_input(self):
        blankinput = {'topic_link': "https://testsite.org/index.php?topic=123456.0", 'creator': None,
                      'creator_link': None, 'views': None, 'replies': None, 'last_post': None, 'url': None,
                      'board_accessed': None, 'title': None
                      }

        blankoutput = parse_basic(blankinput)

        self.assertEqual(blankoutput['creator'], None)
        self.assertEqual(blankoutput['creator_id'], None)
        self.assertEqual(blankoutput['views'], None)
        self.assertEqual(blankoutput['replies'], None)
        self.assertEqual(blankoutput['board_id'], None)
        self.assertEqual(blankoutput['board_accessed'], None)
        self.assertEqual(blankoutput['title'], None)

    def test_parse_basic_missing_input(self):
        missinginput = {'topic_link': "https://testsite.org/index.php?topic=123456.0"}

        missingoutput = parse_basic(missinginput)

        self.assertEqual(missingoutput['creator'], None)
        self.assertEqual(missingoutput['creator_id'], None)
        self.assertEqual(missingoutput['views'], None)
        self.assertEqual(missingoutput['replies'], None)
        self.assertEqual(missingoutput['board_id'], None)
        self.assertEqual(missingoutput['board_accessed'], None)
        self.assertEqual(missingoutput['title'], None)


class TestParseTitle(TestCase):
    def test_parse_title_normal(self):
        grammar = Path(__file__).parent.parent / "title_gram.lark"
        parser = Lark.open(grammar, start="topic", parser="earley")

        testnormal = parse_title("[GB] ignore GMK PBT test1 test2 | ignore", parser)
        self.assertEqual(['GMK', 'PBT'], testnormal['info_codes'])
        self.assertEqual("test1 test2", testnormal['set_name'])
        self.assertEqual("GB", testnormal['thread_type'])
        self.assertEqual("keycaps", testnormal['product_type'])

        testinv = parse_title("test1 test2 GMK PBT test1 test2", parser)
        self.assertEqual(['GMK', 'PBT'], testinv['info_codes'])
        self.assertEqual("test1 test2", testinv['set_name'])

        testmapped = parse_title("ePBT EnjoyPBT test1 test2", parser)
        self.assertEqual(['EPBT', 'EPBT'], testmapped['info_codes'])

        testtc = parse_title("(GB) ignore GMK PBT test1 test2 | ignore", parser)
        self.assertEqual("GB", testtc['thread_type'])

        testnotc = parse_title("GMK test1 test2", parser)
        self.assertEqual(None, testnotc['thread_type'])

    def test_parse_title_edgecase(self):
        grammar = Path(__file__).parent.parent / "title_gram.lark"
        parser = Lark.open(grammar, start="topic", parser="earley")

        testedge = parse_title("literally unparseable", parser)
        self.assertEqual(None, testedge['info_codes'])
        self.assertEqual(None, testedge['set_name'])
        self.assertEqual(None, testedge['thread_type'])
        self.assertEqual(None, testedge['product_type'])

        testedge = parse_title("[IC] literally unparseable", parser)
        self.assertEqual("IC", testedge['thread_type'])

        with self.assertRaises(ValueError):
            parse_title("", parser)


class TestParseBoard(TestCase):
    def test_parse_board_data(self):
        testinput = [{'topic_link': "https://testsite.org/index.php?topic=111111.0", 'title': "GMK test1"},
                     {'topic_link': "https://testsite.org/index.php?topic=222222.0", 'title': "PBT test2"},
                     {'topic_link': "https://testsite.org/index.php?topic=333333.0", 'title': "IFK test3"}
                     ]
        testoutput = parse_board_data(testinput)
        self.assertEqual(testoutput[0]['topic_id'], "111111")
        self.assertEqual(testoutput[1]['topic_id'], "222222")
        self.assertEqual(testoutput[2]['topic_id'], "333333")
        self.assertEqual(testoutput[0]['set_name'], "test1")
        self.assertEqual(testoutput[1]['set_name'], "test2")
        self.assertEqual(testoutput[2]['set_name'], "test3")
        self.assertEqual(testoutput[0]['creator'], None)


class TestCleanBoard(TestCase):
    def test_clean_board_data(self):
        test_in_file = Path(__file__).parent / "fixtures" / "test_raw_data.csv"
        test_out_file = Path(__file__).parent / "fixtures" / "test_out.csv"
        clean_board_data(in_filepath=test_in_file, out_filepath=test_out_file)

        with open(test_out_file, 'r', encoding="utf-8", newline='') as result_csv:
            result_reader = csv.DictReader(result_csv)
            result_data = [csv_topic for csv_topic in result_reader]

        self.assertEqual(10, len(result_data))
        self.assertEqual("110592", result_data[0]['topic_id'])
        os.remove(test_out_file)


class TestFindPostStats(TestCase):
    def setUp(self):
        test_in_file = Path(__file__).parent / "fixtures" / "test_post_data.json"
        self.test_post_data = mech_io.read_post_json(filepath=test_in_file)

    def test_find_post_stats(self):
        post_stats = find_post_stats(self.test_post_data['post_data'])

        self.assertEqual(25, post_stats['num_posts'])
        self.assertEqual(15, post_stats['num_posters'])
        self.assertEqual(6, post_stats['num_creator_posts'])
        self.assertEqual("14 days, 15:42:35", post_stats['post_25_delta'])
        self.assertTrue(post_stats['post_50_delta'] is None)


class TestFindPostLinks(TestCase):
    def setUp(self):
        test_in_file = Path(__file__).parent / "fixtures" / "test_post_data.json"
        self.test_post_data = mech_io.read_post_json(filepath=test_in_file)

    def test_find_post_links(self):
        post_links = find_post_links(self.test_post_data['fp_links'], self.test_post_data['fp_images'])

        self.assertEqual(8, len(post_links))
        self.assertTrue({'link': "https://mechsandco.com/products/gb-gmk-iconographic",
                         'domain': "mechsandco.com"} in post_links)
        self.assertTrue({'link': "https://en.zfrontier.com/products/gmk-iconographic",
                         'domain': "zfrontier.com"} in post_links)


class TestCleanTopicData(TestCase):
    def setUp(self):
        self.test_db = Path(__file__).parent / "fixtures" / "test_db.db"
        mech_io.db_setup(self.test_db, overwrite=True)
        base_data = mech_io.read_csv(Path(__file__).parent / "fixtures" / "test_clean_data.csv")
        mech_io.db_insert_board_clean(base_data, db=self.test_db)
        self.test_in_file = Path(__file__).parent / "fixtures" / "test_post_data.json"
        self.test_post_data = mech_io.read_post_json(filepath=self.test_in_file)

    def tearDown(self):
        os.remove(self.test_db)

    def test_clean_topic_data(self):
        clean_topic_data(in_filepaths=[self.test_in_file], out_db=self.test_db)

        conn = sqlite3.connect(self.test_db)
        conn.row_factory = sqlite3.Row
        result_data = conn.execute("""SELECT * FROM topic_data WHERE topic_id = '110579'""").fetchall()
        result_links = conn.execute("""SELECT * FROM topic_link WHERE topic_id = '110579'""").fetchall()
        conn.close()

        self.assertEqual("2021-01-07 06:17:25", result_data[0]['topic_created'])
        self.assertEqual("14 days, 15:42:35", result_data[0]['post_25_delta'])
        self.assertEqual("2021-01-23 09:19:34", result_data[0]['topic_accessed'])
        self.assertEqual(8, len(result_links))
        self.assertEqual("https://mechsandco.com/products/gb-gmk-iconographic", result_links[0]['link'])
        self.assertEqual("mechsandco.com", result_links[0]['domain'])
