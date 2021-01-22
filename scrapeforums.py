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
    clean_board_data(infilepath=raw_filepath, outfilepath=clean_filepath)

if input("scrape interest check forum? (Y/N): ").upper() == "Y":
    raw_filepath = base_filepath + "ic_raw.csv"
    clean_filepath = base_filepath + "ic_clean.csv"
    scrape_board("https://geekhack.org/index.php?board=132.", limit_pages=65,
                 request_interval=15, filepath=raw_filepath)
    clean_board_data(infilepath=raw_filepath, outfilepath=clean_filepath)



