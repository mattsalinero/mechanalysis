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

print(parse_titles(["[GB] GMK Red & Blue Samurai (GB Closed)"]))
parse_titles(["[GB] GMK Lunar 🚀 — All Kits Will Be Made; Final Numbers Posted"])
parse_titles(["[GB]Enjoypbt KON MOMO (7.10~7.30)"])

# clean_board_data(in_filepath="data/210121gb_raw.csv", out_filepath="data/210121gb_clean.csv")
# clean_board_data(in_filepath="data/210121ic_raw.csv", out_filepath="data/210121ic_clean.csv")

# test_topics = [110511, 110355]
# # test_topics = [110530, 110511, 110455, 110355, 109403, 109307, 109140, 109000, 108983, 108949]
# scrape_topics("geekhack.org", test_topics, filepath="data/testtopicdata.csv", postdir="data/post_data")
