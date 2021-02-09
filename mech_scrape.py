import requests
import time
import datetime
import csv
import json
import random
import bs4
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
    # TODO: replace board url with base url (see scrape_topics())
    sorts = {'firstpost': ";sort=first_post;desc", 'lastpost': ";sort=last_post;desc", 'default': ""}
    sort_url = sorts[sort]
    # base_url = "https://" + forum_url + "/index.php?board=" board + "."

    scraped_board = []
    topic_per = None
    current_url = board_url + str(0) + sort_url
    session = requests.Session()
    session.get(board_url, timeout=5)
    for x in range(limit_pages):
        # TODO: make topic_per into own function using above session call outside loop to pull metadata/ranges
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
    Internal function to extract topic data out of a single page of results
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
        # TODO: change this to last_post in data structure?
        scrape['lastpost'] = datetime.datetime.strptime(next(lastpost), "%a, %d %B %Y, %H:%M:%S")
        # print(scrape['lastpost'])

        scrape['url'] = page_url
        scrape['accessed'] = datetime.datetime.now().replace(microsecond=0)

        scraped_page.append(scrape)

    return scraped_page


def scrape_topics(forum_url, topic_ids, limit_topics=None, offset=0, limit_date=None, request_interval=10,
                  filepath=None, postdir=None):

    if limit_topics and len(topic_ids) > limit_topics:
        if offset > len(topic_ids):
            print(f"offset of {offset} larger than {len(topic_ids)} provided topics")
            return
        topic_ids = topic_ids[offset:(limit_topics + offset)]
    else:
        topic_ids = topic_ids[:]

    topic_ids = [str(topic_id) for topic_id in topic_ids]

    fields = ['topic_id', 'topic_created', 'accessed']
    if filepath:
        with open(filepath, 'a+', encoding="utf-8", newline='') as csvfile:
            if csvfile.tell() == 0:
                csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
                csvwriter.writeheader()
            else:
                csvfile.seek(0, 0)
                csvreader = csv.DictReader(csvfile)
                if csvreader.fieldnames != fields:
                    print("unexpected fields found in already existing file")
                    return

    session = requests.Session()
    base_url = "https://" + forum_url + "/index.php?topic="
    topic_data = []
    for topic_id in topic_ids:

        current_url = base_url + topic_id + ".0"

        # # use a test local file to check that the format parsing works
        # print("fake scrape: " + current_url)
        # with open("testtopic.html") as test_topic:
        #     soup = BeautifulSoup(test_topic, 'html5lib')

        # access current url for page to scrape
        print("requesting: topic " + topic_id)
        current_page = session.get(current_url, timeout=5)
        soup = BeautifulSoup(current_page.content, 'html5lib')

        current_data = scrape_topic(soup, topic_id)
        current_data_short = dict(topic_id=current_data['topic_id'],
                                  topic_created=current_data['topic_created'],
                                  accessed=current_data['accessed'])
        topic_data.append(current_data_short)

        if postdir:
            json_filepath = postdir + "/topic" + topic_id + "_postdata.json"
            json_data = json.dumps(current_data, indent=4, default=(lambda x: x.__str__()))
            with open(json_filepath, 'w') as pdfile:
                pdfile.write(json_data)

        if filepath:
            with open(filepath, 'a', encoding="utf-8", newline='') as csvfile:
                fields = ['topic_id', 'topic_created', 'accessed']
                csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
                csvwriter.writerow(current_data_short)

        # TODO: implement date limit in scrape_topics()
        # if limit_date:
        #     if current_data[-1]['lastpost'].date() < limit_date:
        #         # break if date limit reached
        #         print("Date limit reached")
        #         break

        # wait to keep request rate low
        if topic_id != topic_ids[-1]:
            time.sleep(random.randint(request_interval//2, request_interval*2))

    print(f"Scraping complete: {len(topic_data)} topics scraped")
    return topic_data


def scrape_topic(topic_soup, topic_id='unknown'):
    """
    Internal function to extract information from a single topic page
    :param topic_soup:
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
    # [print(link) for link in scraped_topic['fp_images']]

    # find data for each post on first page (poster, time, text)
    scraped_posts = []
    for post in posts:
        scraped_post = {}

        post_date = post.find('div', class_="keyinfo").find('div', class_="smalltext").stripped_strings
        scraped_post['post_date'] = datetime.datetime.strptime([post for post in post_date][-1],
                                                               "%a, %d %B %Y, %H:%M:%S »")
        post_er = post.find('div', class_="poster").h4
        if post_er.a.get('href'):
            scraped_post['poster_id'] = post_er.a.get('href').split('=')[-1]
        else:
            scraped_post['poster_id'] = None

        # grabs post content for selected post (recursively)
        def quoteless_content(source):
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

        # scraped_post['post_content'] = post.find('div', class_="post").get_text(" ", strip=True)
        scraped_post['post_content'] = "\n".join(quoteless_content(post.find('div', class_="post")))[:2000]

        scraped_posts.append(scraped_post)

    scraped_topic['post_data'] = scraped_posts

    print(f"  topic contains: {len(scraped_topic['post_data'])} posts")

    scraped_topic['accessed'] = datetime.datetime.now().replace(microsecond=0)

    return scraped_topic