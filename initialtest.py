from ghscrape import *
from forumclean import *

scraped_data = scrape_board("https://geekhack.org/index.php?board=70.", limit_pages=3,
                            request_interval=1, filepath='test.csv')
print(type(scraped_data))

clean_board_data(scraped_data)
