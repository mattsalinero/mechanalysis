import requests
import time
import datetime
import csv
import random
from bs4 import BeautifulSoup


def scrape_board(board_url, limit_pages=10, limit_date=None, request_interval=10, filepath=None, sort='firstpost'):
    """
    Function to scrape topic data from a specified forum board (formatted like GeekHack). Will return the scraped data
    and save to a file the filepath parameter is set.

    :param board_url: string of url in the format "https://geekhack.org/index.php?board=70."
                    - function will append integers to the end to get subsequent pages
    :param limit_pages: int max pages of board to scrape
    :param limit_date: date object of date to scrape to (may overrun by 1 page)
    :param request_interval: int how long on average to wait between requests (randomized)
    :param filepath: if set, will write to specified .csv
    :param sort: 'firstpost', 'lastpost', 'default' supported sorts for request
    :return: list of dicts containing scraped data
    """
    # TODO: implement restriction on input values for sort variable
    sorts = {'firstpost': ";sort=first_post;desc", 'lastpost': ";sort=last_post;desc", 'default': ""}
    sort_url = sorts[sort]

    scraped_board = []
    topic_per = None
    current_url = board_url + str(0) + sort_url
    session = requests.Session()
    session.get(board_url, timeout=5)
    for x in range(limit_pages):
        if topic_per:
            current_url = board_url + str(x * topic_per) + sort_url

        # use a test local file to check that the format parsing works
        # print("fake scrape: " + current_url)
        # with open("gbnp.html") as test_board:
        #     soup = BeautifulSoup(test_board, 'html5lib')

        # access current url for page to scrape
        print("requesting: " + current_url)
        current_page = session.get(current_url, timeout=5)
        soup = BeautifulSoup(current_page.content, 'html5lib')

        current_data = scrape_page(soup, current_url)

        if scraped_board:
            if current_data[-1]['topiclink'] == scraped_board[-1]['topiclink']:
                # break if duplicate page received
                print("End of board reached")
                break

        scraped_board.extend(current_data)

        topic_count = len(soup.find('div', class_="tborder topic_table").tbody
                          .find_all('tr', class_=None))
        if topic_per:
            if topic_count < topic_per:
                # break if latest page has fewer topics than the others (i.e. it's the last page)
                print("End of board reached")
                break
        else:
            topic_per = topic_count
        if limit_date:
            if current_data[-1]['lastpost'].date() < limit_date:
                # break if date limit reached
                print("Date limit reached")
                break

        # wait to keep request rate low
        if x != (limit_pages - 1):
            time.sleep(random.randint(request_interval//2, request_interval*2))

    # save to file if appropriate
    if filepath:
        with open(filepath, 'w', encoding="utf-8", newline='') as csvfile:
            fields = ['title', 'topiclink', 'creator', 'creatorlink', 'replies', 'views', 'lastpost', 'url', 'accessed']
            csvwriter = csv.DictWriter(csvfile, fieldnames=fields)

            csvwriter.writeheader()
            csvwriter.writerows(scraped_board)

    print(f"Scraping complete: {len(scraped_board)} topics found")
    return scraped_board


def scrape_page(page_soup, page_url='unknown'):
    """
    Internal function to scrape topic data out of a single page of results
    :param page_soup:
    :param page_url:
    :return:
    """
    scraped_page = []
    topics = page_soup.find('div', class_="tborder topic_table").table.tbody
    for topic in topics.find_all('td', class_=["subject windowbg2", "subject lockedbg2"]):
        scrape = {}
        scrape['title'] = topic.span.a.string
        scrape['topiclink'] = topic.span.a['href']
        if topic.p.a:
            scrape['creator'] = topic.p.a.string
            scrape['creatorlink'] = topic.p.a['href']
        else:
            scrape['creator'] = 'banned user'
            scrape['creatorlink'] = None

        stats_block = topic.parent.find('td', class_=["stats windowbg", "stats lockedbg"]).stripped_strings
        scrape['replies'] = next(stats_block)
        scrape['views'] = next(stats_block)
        # print(scrape['replies'] + ' ' + scrape['views'])

        lastpost = topic.parent.find('td', class_=["lastpost windowbg2", "lastpost lockedbg2"]).stripped_strings
        scrape['lastpost'] = datetime.datetime.strptime(next(lastpost), "%a, %d %B %Y, %H:%M:%S")
        # print(scrape['lastpost'])

        scrape['url'] = page_url
        scrape['accessed'] = datetime.datetime.now().replace(microsecond=0)

        scraped_page.append(scrape)

    return scraped_page


def scrape_topics(forum_url, topic_ids, limit_topics=None, limit_date=None, request_interval=10, filepath=None):

    if limit_topics and len(topic_ids) > limit_topics:
        topic_ids = topic_ids[:limit_topics]
    else:
        topic_ids = topic_ids[:]

    session = requests.Session()
    base_url = forum_url + "/index.php?topic="
    topic_data = []
    for topic_id in topic_ids:

        current_url = base_url + topic_id + ".0"

        # use a test local file to check that the format parsing works
        # print("fake scrape: " + current_url)
        # with open("testtopic.html") as test_topic:
        #     soup = BeautifulSoup(test_topic, 'html5lib')

        # access current url for page to scrape
        print("requesting: topic " + topic_id)
        current_page = session.get(current_url, timeout=5)
        soup = BeautifulSoup(current_page.content, 'html5lib')

        # TODO: define scrape_topic() function
        current_data = scrape_topic(soup, current_url)

        topic_data.append(current_data)

        # TODO: implement date limit in scrape_topics()
        # if limit_date:
        #     if current_data[-1]['lastpost'].date() < limit_date:
        #         # break if date limit reached
        #         print("Date limit reached")
        #         break

        # wait to keep request rate low
        if topic_id != topic_ids[-1]:
            time.sleep(random.randint(request_interval//2, request_interval*2))

    if filepath:
        with open(filepath, 'w', encoding="utf-8", newline='') as csvfile:
            # TODO: fix fields structure with correct field names
            fields = ['title', 'topiclink', 'creator', 'creatorlink', 'replies', 'views', 'lastpost', 'url', 'accessed']
            csvwriter = csv.DictWriter(csvfile, fieldnames=fields)

            csvwriter.writeheader()
            csvwriter.writerows(topic_data)

    print(f"Scraping complete: {len(topic_data)} topics scraped")
    return topic_data
