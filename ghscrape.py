# Initial level is just to scrape from the forum titles, then maybe try to scrape into the posts in a future round.
# Will have to scrape from a search query -> so that I can get the date the post was created.
# This will also yield the post ids needed to access specific posts
#
# Scrapeable from search page:
#     - board title (ex. "Group Buys and Preorders")
#     - topic link
#     - topic title
#     - creator link
#     - creator name
#     - topic created timestamp
#
# Scrapeable from forum list:
#     - board title
#     - topic link
#     - topic title
#     - creator link
#     - creator name
#     - topic views
#     - topic replies
#     - last reply timestamp
#     - (last replier link)
#     - (last replier name)

import requests
import time
import csv
from bs4 import BeautifulSoup


def scrape_board(board_url, limit_pages=10, limit_date=None, request_interval=10, filepath=None):
    """
    Function to scrape topic data from a specified forum board (formatted like GeekHack). Will return the scraped data
    and save to a file the filepath parameter is set.

    :param board_url: string of url in the format "https://geekhack.org/index.php?board=70."
                    - function will append integers to get subsequent pages
    :param limit_pages: int max pages to get
    :param limit_date: (not implemented)
    :param request_interval: int how long on average to wait between requests (randomized)
    :param filepath:
    :return:
    """
    scraped_board = []
    topic_per = None
    current_url = board_url + str(0)
    for x in range(limit_pages):
        if topic_per:
            current_url = board_url + str(x * topic_per)

        # use a test local file to check that the format parsing works
        print("fake scrape: " + current_url)
        with open("gbnp.html") as test_board:
            soup = BeautifulSoup(test_board, 'html5lib')

        # print("requesting: " + current_url)
        # current_page = requests.get(current_url)
        # soup = BeautifulSoup(current_page.content, 'html5lib')

        current_data = scrape_page(soup, current_url)
        scraped_board.extend(current_data)

        topic_count = len(soup.find('div', class_="tborder topic_table").tbody
                          .find_all('tr', class_=None))
        if topic_per:
            if topic_count < topic_per:
                # break if latest page has fewer topics than the others
                print("End of board reached")
                break
        else:
            topic_per = topic_count

        if x != (limit_pages - 1):
            time.sleep(request_interval)

    if filepath:
        with open(filepath, 'w', encoding="utf-8", newline='') as csvfile:
            fields = ['title', 'topiclink', 'creator', 'creatorlink', 'replies', 'views', 'lastpost', 'url']
            csvwriter = csv.DictWriter(csvfile, fieldnames=fields)

            csvwriter.writeheader()
            csvwriter.writerows(scraped_board)

    print(f"Scraping complete: {len(scraped_board)} topics found")
    return scraped_board


# Build this section out into a function that also takes a URL and inserts that into the scraped data
# This function would work to extract data out of a single soup
# (then would loop over this to extract from multiple pages)
def scrape_page(page_soup, page_url='unknown'):
    """

    :param page_soup:
    :param page_url:
    :return:
    """
    scraped_page = []
    topics = page_soup.find('div', class_="tborder topic_table").table.tbody
    for topic in topics.find_all('td', class_="subject windowbg2"):
        scrape = {}
        scrape['title'] = topic.span.a.string
        scrape['topiclink'] = topic.span.a['href']
        scrape['creator'] = topic.p.a.string
        scrape['creatorlink'] = topic.p.a['href']

        stats_block = topic.parent.find('td', class_="stats windowbg").stripped_strings
        scrape['replies'] = next(stats_block)
        scrape['views'] = next(stats_block)
        # print(scrape['replies'] + ' ' + scrape['views'])

        lastpost = topic.parent.find('td', class_="lastpost windowbg2").stripped_strings
        scrape['lastpost'] = next(lastpost)
        # print(scrape['lastpost'])

        scrape['url'] = page_url

        scraped_page.append(scrape)

    return scraped_page
# remember to extend() for each page (not append())


# this section actually grabs the live data from gh -> test with offline html
# gbnp_url = "https://geekhack.org/index.php?board=70."
# board = requests.get(gbnp_url)
# print(board.url)
# soup = BeautifulSoup(board.content, 'html5lib')

# use a test local file to check that the format parsing works
with open("gbnp.html") as test_board:
    soup = BeautifulSoup(test_board, 'html5lib')

scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=3,
                            request_interval=1, filepath='test.csv')

# print(soup.tbody.prettify())
