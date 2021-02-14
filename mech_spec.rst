===============
 MECH ANALYSIS
===============
| Author:
| Created: 2021-01-11
| Last Update: N/A

----

**OVERVIEW**

Over the last ~five years, the community of mechanical keyboard enthusiasts has experienced rapid growth, centered around dedicated community forums, subreddits, and content creator communities. Currently, participating in the MK hobby involves researching, preordering, waiting for, and assembling exclusive and/or limited stock keyboards and keyboard components, talking about the above, and (occasionally) using the keyboards for typing. Being relatively young, the MK hobby lacks clear industry leaders for creation of these exclusive components and instead many popular components (specifically, many keycap sets) are financed using a group-buy system on community forums and subreddits. This project will attempt to analyze data on one class of component (keycaps) to determine year over year statistics and trends within the MK hobby.

**TERMINOLOGY (TBC)**

**CONTEXT**

Currently, data on the success or failure rate of keycap group buys is not readily accessible and much information is buried in individual threads or posts on the aformentioned community forums. Clear trends present in the publically available data could be used by aspiring designers to inform their choices when attempting to realize their own keycap set.

**GOALS**

- Interface with and scrape GeekHack to retrieve available data from:

  - Group Buy topic titles
  - Group Buy topic content (for selected topics only)
  - Interest Check topic titles
  - Interest Check topic content (for selected topics only)

- Analyze data to determine (at minimum):

  - Which topics relate to keycap sets (vs. other out of scope products)
  - Title of the set
  - Infocodes for the set
  - Date of original Group Buy post
  - Interest measures of set (topic replies and views)
  - Link (if any) between Group Buy and Interest Check topics for set

**OUT OF SCOPE**

Analysis of components other than keycaps (ex. switches, keyboard chassis).

**EXTENSIONS**

- Additional data types:

  - Classifieds post data (for post-group buy interest in sets)
  - Further topic content analysis:

    - Number of kits per buy
    - Number/distribution of different vendors

- Other data sources (such as reddit)
- Automatic data intake and publishing:

  - Public dashboard/report
  - Automated intake and processing of data for dashboard

----

**PROPOSED SOLUTION**

*DATA ACQUISITION*

Initial data acquisition will be performed via web scraping of GeekHack. As the project is focused on the effects/outcomes of activities on these community forums, acquiring the available data straight from this source provides the best chance of capturing relevant information. The webscraper will be implemented using Beautifulsoup4 and Requests and save scraped data to a .csv for later analysis.

The webscraper will first take in topic titles from the Group Buy and Interest Check forums. Then, initial data processing will be performed on the scraped topics to identify relevant topics. Only these topics will be individually accessed for scraping data from the topic page (as this has to happen on a per-post basis and generates many requests).

*DATA STORAGE*

Data storage will be accomplished using two systems

SQLite Schema

	board_raw
		id INTEGER PRIMARY KEY,
		title VARCHAR,
		topic_link VARCHAR,
		creator VARCHAR,
		creator_link VARCHAR,
		replies VARCHAR,
		views VARCHAR, 
		last_post VARCHAR,
		url VARCHAR,
		accessed VARCHAR -> datetime

	page_raw
		topic_id INTEGER PRIMARY KEY, -> topic_id now a number
		topic_created VARCHAR, -> datetime
		topic_accessed VARCHAR -> datetime

	page_link
		id INTEGER PRIMARY KEY,
		topic_id INTEGER NOT NULL,
		link VARCHAR NOT NULL

	page_image
		id INTEGER PRIMARY KEY,
		topic_id INTEGER NOT NULL,
		image_source VARCHAR NOT NULL

	??post_raw??

	topic_data
		topic_id INTEGER PRIMARY KEY,
		product_type VARCHAR,
		thread_type VARCHAR,
		set_name VARCHAR,
		creator VARCHAR,
		creator_id INTEGER,
		views INTEGER,
		replies INTEGER,
		board INTEGER,
		board_accessed VARCHAR, -> datetime
		title VARCHAR

	??topic_page_data??
		topic_id INTEGER PRIMARY KEY,
		topic_created VARCHAR, -> datetime
		topic_accessed VARCHAR -> datetime
		nonimage_links INTEGER

	topic_icode
		id INTEGER PRIMARY KEY,
		topic_id INTEGER NOT NULL,
		info_code VARCHAR NOT NULL

File based system

*DATA PROCESSING*

Data processing will likely form the bulk of this project. As the scraped data is largely forum posts (and the associated metadata), important information is combined into unstructured data fields (such as topic title). GeekHack has conventions for group buys and interest checks that are loosely adhered to (such as [GB] tags and commonly used abbreviations for keycap profiles and manufacturers). To extract relevant features from the unstructured fields, the project will implement a parser using a grammar adapted to recognize keycap set-specific terminology. At minimum, this implementation should extract infocodes and set titles from the topic title of a post.

Additionally, the data processing stage includes linking group buy posts with any related interest check posts. This linking can be based on the posting user and/or set title.

*DATA ANALYSIS*

This stage is planned to largely take place in Jupyter and will initially produce a one-off report (with nice graphs). As discussed in the extension section, any useful statistics found in exploratory data analysis may be later formalized into a dashboard.

**TEST PLAN (TBC)**

----

**RISKS**

Geekhack is a relatively small site and there is a potential to overscrape (especially when having to access individual topics). Care should be taken to minimize the number of topics accessed in this way. As this is a side project, other obligations could get in the way of desired timelines for completion.

**TASKS/MILESTONES**

- Revise web scraper to scrape topic content (given list of topic IDs), implement intermediate saving of scraped data, and handle/log request failure. (*2021-01-15*)
- Refactor proof-of-concept parser to implement more robust parsing algorithm (no more regex). (*2021-01-17*)
- Scrape all required data (including individual topic posts). (*2021-01-20*)
- Perform exploratory data analysis on gathered and processed data and produce report. (*2021-01-24*)
