import datetime
from forumclean import *
from unittest import TestCase


class TestParseBasic(TestCase):
    def test_parse_basic_row_topic_id(self):
        testinput = {'topiclink': "https://testsite.org/index.php?topic=123456.0"}
        self.assertEqual(parse_basic_row(testinput)['topic_id'], "123456")

    def test_parse_basic_row_bad_topic_id(self):
        blankinput = {'topiclink': None, 'creator': None, 'creatorlink': None, 'views': None, 'replies': None,
                      'lastpost': None, 'url': None, 'accessed': None, 'title': None}
        with self.assertRaises(ValueError):
            parse_basic_row(blankinput)
        with self.assertRaises(ValueError):
            parse_basic_row({})

    def test_parse_basic_row_proper_input(self):
        testinput = {'title': "test title",
                     'topiclink': "https://testsite.org/index.php?topic=123456.0",
                     'creator': "test creator",
                     'creatorlink': "https://testsite.org/index.php?action=profile;u=123456",
                     'replies': "123 Replies",
                     'views': "456 Views",
                     'lastpost': datetime.datetime.fromisoformat("2001-01-01 01:01:01"),
                     'url': "https://geekhack.org/index.php?board=70.0;sort=first_post;desc",
                     'accessed': datetime.datetime.fromisoformat("2002-02-02 02:02:02")
                     }

        testoutput = parse_basic_row(testinput)

        self.assertEqual(testoutput['creator'], "test creator")
        self.assertEqual(testoutput['creator_id'], "123456")
        self.assertEqual(testoutput['views'], 456)
        self.assertEqual(testoutput['replies'], 123)
        self.assertEqual(testoutput['board'], "70")
        self.assertEqual(testoutput['access_date'], datetime.datetime.fromisoformat("2002-02-02 02:02:02"))
        self.assertEqual(testoutput['title'], "test title")

    def test_parse_basic_row_blank_input(self):
        blankinput = {'topiclink': "https://testsite.org/index.php?topic=123456.0", 'creator': None,
                      'creatorlink': None, 'views': None, 'replies': None, 'lastpost': None, 'url': None,
                      'accessed': None, 'title': None
                      }

        blankoutput = parse_basic_row(blankinput)

        self.assertEqual(blankoutput['creator'], None)
        self.assertEqual(blankoutput['creator_id'], None)
        self.assertEqual(blankoutput['views'], None)
        self.assertEqual(blankoutput['replies'], None)
        self.assertEqual(blankoutput['board'], None)
        self.assertEqual(blankoutput['access_date'], None)
        self.assertEqual(blankoutput['title'], None)

    def test_parse_basic_row_missing_input(self):
        missinginput = {'topiclink': "https://testsite.org/index.php?topic=123456.0"}

        missingoutput = parse_basic_row(missinginput)

        self.assertEqual(missingoutput['creator'], None)
        self.assertEqual(missingoutput['creator_id'], None)
        self.assertEqual(missingoutput['views'], None)
        self.assertEqual(missingoutput['replies'], None)
        self.assertEqual(missingoutput['board'], None)
        self.assertEqual(missingoutput['access_date'], None)
        self.assertEqual(missingoutput['title'], None)


class TestParseTitle(TestCase):
    def test_parse_title_normal(self):
        grammar = Path(__file__).parent.parent / "gb_title.lark"
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
        grammar = Path(__file__).parent.parent / "gb_title.lark"
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


class TestParseTopic(TestCase):
    def test_parse_topic_data(self):
        testinput = [{'topiclink': "https://testsite.org/index.php?topic=111111.0", 'title': "GMK test1"},
                     {'topiclink': "https://testsite.org/index.php?topic=222222.0", 'title': "PBT test2"},
                     {'topiclink': "https://testsite.org/index.php?topic=333333.0", 'title': "IFK test3"}
                     ]
        testoutput = parse_topic_data(testinput)
        self.assertEqual(testoutput[0]['topic_id'], "111111")
        self.assertEqual(testoutput[1]['topic_id'], "222222")
        self.assertEqual(testoutput[2]['topic_id'], "333333")
        self.assertEqual(testoutput[0]['set_name'], "test1")
        self.assertEqual(testoutput[1]['set_name'], "test2")
        self.assertEqual(testoutput[2]['set_name'], "test3")
        self.assertEqual(testoutput[0]['creator'], None)
