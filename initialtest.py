from ghscrape import *
from forumclean import *

# scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=3,
#                             request_interval=10, filepath='test.csv')
# print(type(scraped_data))

# testdata = clean_board_data(scraped_data, filepath="data/test2.csv")
#
# print(testdata[['code', 'name']].head(45))

# print(find_captype("[GB] TGR-Jane v2 CE (QC, Shipping) 50% completed "))
# print(find_captype("[GB]Enjoypbt '紺桃KON MOMO' Japanese keycaps (7.10~7.30)"))

# scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=5,
#                             request_interval=15, filepath="data/210108testraw.csv")

# testdata = clean_board_data(scraped_data, filepath="data/210108test.csv")

parse_title("[GB] GMK Evil Dolch😈 | Final Numbers!")

"[GB] GMK Evil Dolch | Final Numbers! 😈"
