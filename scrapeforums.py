from ghscrape import *
from forumclean import *
import datetime


date_code = datetime.datetime.now().strftime("%y%m%d")
base_filepath = "data/" + date_code

print("Scraping data for " + date_code)

if input("scrape groupbuy forum? (Y/N): ").upper() == "Y":
    raw_filepath = base_filepath + "gb_raw.csv"
    clean_filepath = base_filepath + "gb_clean.csv"
    scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=40,
                 request_interval=15, filepath=raw_filepath)
    clean_board_data(in_filepath=raw_filepath, out_filepath=clean_filepath)

if input("scrape interest check forum? (Y/N): ").upper() == "Y":
    raw_filepath = base_filepath + "ic_raw.csv"
    clean_filepath = base_filepath + "ic_clean.csv"
    scrape_board("https://geekhack.org/index.php?board=132.", limit_pages=65,
                 request_interval=15, filepath=raw_filepath)
    clean_board_data(in_filepath=raw_filepath, out_filepath=clean_filepath)

if input("scrape groupbuy topics? (Y/N): ").upper() == "Y":
    num_topics = int(input("enter number of topics to scrape: "))
    offset = int(input("enter offset: "))
    date_code = input("enter datecode of topics to scrape: ")
    topiclist_path = "data/" + date_code + "topiclist.csv"
    with open(topiclist_path, 'r', encoding="utf-8", newline='') as csvfile:
        topic_reader = csv.DictReader(csvfile)
        topic_ids = [row['topic_id'] for row in topic_reader]

    topic_path = base_filepath + "td.csv"
    scrape_topics("geekhack.org", topic_ids, limit_topics=num_topics, offset=offset, filepath=topic_path,
                  postdir="data/post_data")
