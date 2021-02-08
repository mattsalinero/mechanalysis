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
        parser = Lark.open("gb_title.lark", start="topic", parser="earley")
        self.fail()

    def test_parse_title_inverted(self):
        self.fail()

    def test_parse_title_mapping(self):
        self.fail()

    def test_parse_title_threadcode(self):
        self.fail()

    def test_parse_title_unknown(self):
        self.fail()
