import requests
import time
import datetime
import csv
import random
from bs4 import BeautifulSoup


def scrape_board(board_url, limit_pages=10, limit_date=None, request_interval=10, filepath=None):
    """
    Function to scrape topic data from a specified forum board (formatted like GeekHack). Will return the scraped data
    and save to a file the filepath parameter is set.

    :param board_url: string of url in the format "https://geekhack.org/index.php?board=70."
                    - function will append integers to get subsequent pages
    :param limit_pages: int max pages of board to scrape
    :param limit_date: date object of date to scrape to (may overrun by 1 page)
    :param request_interval: int how long on average to wait between requests (randomized)
    :param filepath: if set, will write to specified .csv
    :return: list of dicts containing scraped data
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

        # access current url for page to scrape
        # print("requesting: " + current_url)
        # current_page = requests.get(current_url)
        # soup = BeautifulSoup(current_page.content, 'html5lib')

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
    Internal function to scrape topic data out of a single page
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
        scrape['creator'] = topic.p.a.string
        scrape['creatorlink'] = topic.p.a['href']

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


scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=3,
                            request_interval=1, filepath='test.csv')

# print(soup.tbody.prettify())
