from mech_scrape import *
from mech_scrape import _board_topic_count
import unittest
from unittest import TestCase


class TestScrapeBoard(TestCase):
    @unittest.expectedFailure
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


class TestScrapePost(TestCase):
    def test_scrape_post(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_post.html"
        with open(test_filepath) as test_post:
            post_soup = BeautifulSoup(test_post, 'html5lib')
        test_post_data = scrape_post(post_soup)

        self.assertEqual(datetime.datetime.strptime("Sat, 03 October 2020, 13:58:45", "%a, %d %B %Y, %H:%M:%S"),
                         test_post_data['post_date'])
        self.assertEqual("52009", test_post_data['poster_id'])
        self.assertEqual("More\n<--\nprogress", test_post_data['post_content'])


class TestScrapeTopic(TestCase):
    def test_scrape_topic(self):
        test_filepath = Path(__file__).parent / "fixtures" / "test_topic.html"
        with open(test_filepath) as test_topic:
            topic_soup = BeautifulSoup(test_topic, 'html5lib')
        test_topic_data = scrape_topic(topic_soup)

        self.assertEqual(datetime.datetime.strptime("Sun, 20 September 2020, 15:19:57", "%a, %d %B %Y, %H:%M:%S"),
                         test_topic_data['topic_created'])
        self.assertEqual(35, len(test_topic_data['fp_links']))
        self.assertEqual("https://i.imgur.com/RA9tqCc.png", test_topic_data['fp_links'][0])
        self.assertEqual(27, len(test_topic_data['fp_images']))
        self.assertEqual("https://i.imgur.com/RA9tqCc.png", test_topic_data['fp_links'][0])
        self.assertEqual(15, len(test_topic_data['post_data']))


class TestScrapeTopics(TestCase):
    @unittest.expectedFailure
    def test_scrape_topics(self):
        self.fail()
