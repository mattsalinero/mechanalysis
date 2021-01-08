from ghscrape import *
from forumclean import *

# scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=3,
#                             request_interval=1, filepath='test.csv')
# print(type(scraped_data))
#
# clean_board_data(scraped_data)

print(find_captype("[GB] TGR-Jane v2 CE (QC, Shipping) 50% completed "))
print(find_captype("[GB]Enjoypbt '紺桃KON MOMO' Japanese keycaps (7.10~7.30)"))
