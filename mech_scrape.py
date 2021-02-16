import requests
import time
import datetime
import csv
import json
import random
from pathlib import Path
import mech_io
import bs4
from bs4 import BeautifulSoup


def scrape_board(forum_url, board, page_limit=10, date_limit=None, request_interval=10, filepath=None,
                 sort='first_post'):
    """
    Scrapes topic data from a specified forum board (formatted like GeekHack)
    :param forum_url: string of url in the format "geekhack.org"
                    - function will append integers to the end to get subsequent pages
    :param board: string of board identifier ("70" for group buy)
    :param page_limit: int max pages of board to scrape
    :param date_limit: date object of date to scrape to (may overrun by 1 page)
    :param request_interval: int how long on average to wait between requests (randomized)
    :param filepath: if set, will write to specified .csv
    :param sort: 'first_post', 'last_post', 'default' supported sorts for request
    :return: list of dicts containing scraped data
    """
    # TODO: implement restriction on input values for sort variable
    base_url = "https://" + forum_url + "/index.php?board=" + board + "."
    sorts = {'first_post': ";sort=first_post;desc", 'last_post': ";sort=last_post;desc", 'default': ""}
    sort_url = sorts[sort]

    session = requests.Session()

    first_page = session.get(base_url, timeout=5)
    expected_topics = _board_topic_count(BeautifulSoup(first_page.content, 'html5lib'))
    scraped_board = []
    for x in range(page_limit):
        current_url = base_url + str(x * expected_topics) + sort_url

        # access current url for page to scrape
        print("requesting: " + current_url)
        current_page = session.get(current_url, timeout=5)
        soup = BeautifulSoup(current_page.content, 'html5lib')

        current_data = scrape_page(soup, current_url)

        if x > 0:
            if current_data[-1]['topic_link'] == scraped_board[-1]['topic_link']:
                # break if duplicate page received
                print("End of board reached")
                break

        scraped_board.extend(current_data)

        topic_count = _board_topic_count(soup)
        if topic_count < expected_topics:
            # break if latest page has fewer topics than the others (i.e. it's the last page)
            print("End of board reached")
            break

        if date_limit:
            if current_data[-1]['last_post'].date() < date_limit:
                # break if date limit reached
                print("Date limit reached")
                break

        # wait to keep request rate low
        if x != (page_limit - 1):
            time.sleep(random.randint(request_interval // 2, request_interval * 2))

    # save to file if appropriate
    if filepath:
        fields = ['title', 'topic_link', 'creator', 'creator_link', 'replies', 'views', 'last_post', 'url',
                  'board_accessed']
        mech_io.write_csv(scraped_board, filepath, fields)

    print(f"Scraping complete: {len(scraped_board)} topics found")
    return scraped_board


def scrape_page(page_soup, page_url='unknown'):
    """
    Extracts topic data out of a single page of a board index
    :param page_soup: BeautifulSoup soup of page
    :param page_url: url entry was scraped from (optional)
    :return: entry data as list of dicts
    """
    # TODO: rename this to scrape_entry() or something
    scraped_page = []
    topics = page_soup.find('div', class_="tborder topic_table").table.tbody
    for topic in topics.find_all('td', class_=["subject windowbg2", "subject lockedbg2"]):
        scrape = {}

        scrape['title'] = topic.span.a.string
        scrape['topic_link'] = topic.span.a['href']

        # if a user is banned they don't have a corresponding link
        if topic.p.find('a', recursive=False):
            scrape['creator'] = topic.p.a.string
            scrape['creator_link'] = topic.p.a['href']
        else:
            scrape['creator'] = "banned user"
            scrape['creator_link'] = None

        stats_block = topic.parent.find('td', class_=["stats windowbg", "stats lockedbg"]).stripped_strings
        scrape['replies'] = next(stats_block)
        scrape['views'] = next(stats_block)

        lastpost = topic.parent.find('td', class_=["lastpost windowbg2", "lastpost lockedbg2"]).stripped_strings
        scrape['last_post'] = datetime.datetime.strptime(next(lastpost), "%a, %d %B %Y, %H:%M:%S")

        scrape['url'] = page_url
        scrape['board_accessed'] = datetime.datetime.now().replace(microsecond=0)

        scraped_page.append(scrape)

    return scraped_page


def _board_topic_count(soup):
    # finds the number of topics on given board index page
    topic_count = len(soup.find('div', class_="tborder topic_table").tbody
                      .find_all('tr', class_=None))
    return topic_count


def scrape_topics(forum_url, topic_ids, topic_limit=None, offset=0, date_limit=None, request_interval=10,
                  filepath=None, post_dir=None):
    """
    Scrapes data from a specified topic page of a forum (formatted like GeekHack)
    :param forum_url: string of url in the format "geekhack.org"
    :param topic_ids: list of topic ids for desired pages
    :param topic_limit: (optional) maximum number of topics to scrape
    :param offset:
    :param date_limit:
    :param request_interval:
    :param filepath:
    :param post_dir:
    :return:
    """
    # TODO: rework this function to actually return the full data/not aggregate to csv -> when using primarily the
    #  db, having the truncated version isn't useful
    # TODO: get rid of offset and put that functionality in the calling method
    if topic_limit and len(topic_ids) > topic_limit:
        if offset > len(topic_ids):
            print(f"offset of {offset} larger than {len(topic_ids)} provided topics")
            return
        topic_ids = topic_ids[offset:(topic_limit + offset)]
    else:
        topic_ids = topic_ids[:]

    topic_ids = [str(topic_id) for topic_id in topic_ids]

    fields = ['topic_id', 'topic_created', 'topic_accessed']
    if filepath:
        mech_io.prepare_appending_csv(filepath, fields)

    session = requests.Session()
    base_url = "https://" + forum_url + "/index.php?topic="
    topic_data = []
    for topic_id in topic_ids:

        current_url = base_url + topic_id + ".0"

        # access current url for page to scrape
        print("requesting: topic " + topic_id)
        current_page = session.get(current_url, timeout=5)
        soup = BeautifulSoup(current_page.content, 'html5lib')

        current_data = scrape_topic(soup, topic_id)
        current_data_short = dict(topic_id=current_data['topic_id'],
                                  topic_created=current_data['topic_created'],
                                  topic_accessed=current_data['topic_accessed'])
        topic_data.append(current_data_short)

        if post_dir:
            # TODO: implement default postdir using pathlib
            # TODO: rework arguments to have separate arguments for using a method to save and the place to save
            mech_io.write_post_json(topic_id, current_data, folder=post_dir)

        if filepath:
            # TODO: implement default filepath using pathlib
            mech_io.append_csv(current_data_short, filepath, fields)

        # TODO: implement date limit in scrape_topics()
        # if limit_date:
        #     if current_data[-1]['lastpost'].date() < limit_date:
        #         # break if date limit reached
        #         print("Date limit reached")
        #         break

        # wait to keep request rate low
        if topic_id != topic_ids[-1]:
            time.sleep(random.randint(request_interval // 2, request_interval * 2))

    print(f"Scraping complete: {len(topic_data)} topics scraped")
    return topic_data


def scrape_topic(topic_soup, topic_id='unknown'):
    """
    Extracts information from a single topic page
    :param topic_soup: BeautifulSoup soup of topic page
    :param topic_id: topic id to associate with extracted data
    :return: dict of extracted topic data
    """
    scraped_topic = {'topic_id': topic_id}

    # get the posts in the topic
    posts = topic_soup.find('div', id="forumposts").find(id="quickModForm").find_all('div', class_="post_wrapper")
    first_post = posts[0]

    # find data specific to first post (topic created date, full lists of links, images)
    date_created = first_post.find('div', class_="keyinfo").find('div', class_="smalltext").stripped_strings
    scraped_topic['topic_created'] = datetime.datetime.strptime((' '.join([text for text in date_created])),
                                                                "« on: %a, %d %B %Y, %H:%M:%S »")
    first_post_links = first_post.find('div', class_="post").find_all('a')
    scraped_topic['fp_links'] = [link.get('href') for link in first_post_links]
    first_post_images = first_post.find('div', class_="post").find_all('img')
    scraped_topic['fp_images'] = [img.get('src') for img in first_post_images]

    print(f"  topic created: {scraped_topic['topic_created']}")
    print(f"  topic contains: {len(scraped_topic['fp_links'])} links")
    print(f"  topic contains: {len(scraped_topic['fp_images'])} images")

    # find data for each post on first page (poster, time, text)
    scraped_posts = []
    for post in posts:
        scraped_posts.append(scrape_post(post))

    scraped_topic['post_data'] = scraped_posts

    print(f"  topic contains: {len(scraped_topic['post_data'])} posts")

    scraped_topic['topic_accessed'] = datetime.datetime.now().replace(microsecond=0)

    return scraped_topic


def scrape_post(post):
    """
    Extracts information from a post within a topic page
    :param post: BeautifulSoup soup of post
    :return: dict of extracted post data
    """
    scraped_post = {}

    post_date = post.find('div', class_="keyinfo").find('div', class_="smalltext").stripped_strings
    scraped_post['post_date'] = datetime.datetime.strptime([date for date in post_date][-1],
                                                           "%a, %d %B %Y, %H:%M:%S »")
    post_er = post.find('div', class_="poster").h4
    if post_er.a.get('href'):
        scraped_post['poster_id'] = post_er.a.get('href').split('=')[-1]
    else:
        scraped_post['poster_id'] = None

    def quoteless_content(source):
        # grabs post content for selected post (recursively), excluding quoted text of earlier posts
        content = []
        for child in source.children:
            if isinstance(child, bs4.element.NavigableString):
                string_content = str(child).strip()
                if string_content:
                    content.append(string_content)
                continue
            elif child.name == "blockquote":
                content.append("[quoted text]")
                continue
            else:
                child_content = quoteless_content(child)
                if child_content:
                    content.extend(child_content)
        return content

    scraped_post['post_content'] = "\n".join(quoteless_content(post.find('div', class_="post")))[:2000]

    return scraped_post
