from ghscrape import *
from forumclean import *
import csv

# scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=40,
#                             request_interval=15, filepath="data/210109raw.csv")
# scraped_data = scrape_board("https://geekhack.org/index.php?board=132.", limit_pages=65,
#                             request_interval=15, filepath="data/210109ic_raw.csv")

# rawdata = pd.read_csv("data/210109raw.csv")
# clean_data = clean_board_data(rawdata, "data/210109gb_clean.csv")
rawdata = pd.read_csv("data/210109ic_raw.csv")
clean_data = clean_board_data(rawdata, "data/210109ic_clean.csv")


