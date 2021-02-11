from mech_scrape import *
from mech_scrape import _board_topic_count
from unittest import TestCase


class TestScrapeBoard(TestCase):
    def test_scrape_board(self):
        self.fail()


class TestScrapePage(TestCase):
    def test_scrape_page(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_board_index.html"
        with open(test_filepath) as test_board:
            soup = BeautifulSoup(test_board, 'html5lib')
        test_output = scrape_page(soup, "test_url")
        self.assertEqual(10, len(test_output))
        self.assertEqual("[GB] 7V - 75% Keyboard by gok (IN PRODUCTION)", test_output[0]['title'])
        self.assertEqual("https://geekhack.org/index.php?topic=105685.0", test_output[0]['topic_link'])
        self.assertEqual("gok101", test_output[0]['creator'])
        self.assertEqual("https://geekhack.org/index.php?action=profile;u=66635", test_output[0]['creator_link'])
        self.assertEqual("352 Replies", test_output[0]['replies'])
        self.assertEqual("93377 Views", test_output[0]['views'])
        self.assertEqual(datetime.datetime.strptime("Mon, 04 January 2021, 22:48:20", "%a, %d %B %Y, %H:%M:%S"),
                         test_output[0]['last_post'])
        self.assertEqual("test_url", test_output[0]['url'])
        self.assertEqual(type(datetime.datetime.now()), type(test_output[0]['accessed']))
        self.assertEqual("banned user", test_output[1]['creator'])
        self.assertEqual(None, test_output[1]['creator_link'])


class TestTopicCount(TestCase):
    def test_board_topic_count(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_board_index.html"
        with open(test_filepath) as test_board:
            soup = BeautifulSoup(test_board, 'html5lib')
        self.assertEqual(15, _board_topic_count(soup))
