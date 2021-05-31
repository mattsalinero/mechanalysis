# Mechanical  Keyboard Analysis Project

Creator: Matt Salinero

Created: 2021-01-11

Last Updated: 2021-05-29

---
## Project Overview

*TBC*

---
## Task

This project will attempt to analyze data on keycap group buys listed on community websites to identify year over year trends.

### Context
Over the last \~five years the mechanical keyboard hobby has experienced rapid growth. Being a mechanical keyboard enthusiast involves researching, preordering, waiting for, and assembling exclusive mechanical keyboards from limited run keyboard components (such as keycaps, keyboard chassis, and switches). Also, mechanical keyboards can be typed on! 

Currently, the mechanical keyboard industry lacks clear corporate leaders designing and selling enthusiast-level components. Instead, the manufacture of components is often financed using a group buy system that relies on the community preordering components to cover manufacturing costs. These group buys are often advertized on dedicated community forums, subreddits, and content creator communities dedicated to mechanical keyboards. 

However, despite the group buys being publicly advertized, data on the success or failure rate of group buys is not readily accessible. Much of tha available information is buried in unstructured forum threads or posts. Clear trends present in the publically available data could be used by aspiring designers to inform their choices when attempting to realize their own keycap set.

### Terminology 

*TBC*

- group buy
- interest check
- keycap
- keycap profile
- keycap material
- keycap manufacturer
- infocode
- keyset
- topic index (forum)
- topic (forum)
- post (forum)

### Project Goals
Analysis in this project will focus on determining:
- How many keysets have been released/advertised
- Corresponding keyset names and infocodes
- Date of group buy for each keyset
- Interest metrics for each keyset (such as topic replies and views)
- Statistical link (if any) between popularity of group buy and popularity of interest check for each keyset

### Out of Scope
Analysis of prebuilt keyboards and keyboard components other than keycaps (ex. switches, keyboard chassis) isn't a part of this project, though potentially the project could eventually be extended to look at those items.

---
## Data Sources

The main data source for this project is publicly available data [geekhack](https://geekhack.org/), a community forum. Relevant data will be acquired by scraping public topic and post contents from geekhack's "group buys and preorders" and "interest checks" forums. As the project is focused on the effects/outcomes of activities on these community forums, acquiring the available data straight from this source provides the best chance of capturing relevant information. The webscraper will use the "beautifulsoup4" and "requests" python libraries to extract and save scraped data for analysis.

To minimize requests to geekhack, scraping will be performed in two stages. First, the scraper will ingest topic titles from group buy/interest check topic index pages and perform initial data processing to identify relevant topics (about keysets). In the second stage, the scraper will access the topic pages for the topics identified in stage one to extract additional data about each relevant topic.

## Data Storage

Collected data will be stored in either files (in the case of raw data for archive) or a database (for processed/cleaned data)

### Raw Data Files
The raw scraped data from topic indexes will be aggregated and stored in .csv files per board scraped. Scraped topic page data will be stored in .json files for each scraped topic.

### Database(using SQLite)
A database will be used to store cleaned and processed data. As this project is only focused on keysets (for the moment), any cleaned data on non-keyset topics (such as data gathered from topic index pages) will be stored. These database entries may be incomplete as no topic page-level data gathering is planned for non-keyset topics. The current database schema is included below.

#### Schema:
```sql
/* Main fact table for topic data */
CREATE TABLE topic_data (
	topic_id VARCHAR PRIMARY KEY,
	topic_created VARCHAR, --datetime value
	product_type VARCHAR,
	thread_type VARCHAR,
	set_name VARCHAR,
	creator VARCHAR,
	creator_id VARCHAR,
	views INTEGER,
	replies INTEGER,
	board_id VARCHAR,
	board_accessed VARCHAR, --datetime value
	title VARCHAR,
	num_posts INTEGER,
	num_posters INTEGER,
	num_creator_posts INTEGER,
	post_25_delta VARCHAR, --time interval
	post_50_delta VARCHAR, --time interval
	topic_accessed VARCHAR --datetime value
	);

/* Topic infocodes (many to one relationship with topics) */
CREATE TABLE topic_icode (
	topic_id VARCHAR NOT NULL,
	info_code VARCHAR NOT NULL,
	PRIMARY KEY (topic_id, info_code),
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);

/* Links contained in topic first post (many to one relationship with topics) */
CREATE TABLE topic_link (
	id INTEGER PRIMARY KEY,
	topic_id VARCHAR NOT NULL,
	link VARCHAR NOT NULL,
	domain VARCHAR, --stores the top level domain for the link
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);
```

---
## Data Cleaning

Some extracted fields have to undergo significant processing before they will be useable in analysis. Scraped forum data includes important information contained in unstructured data fields (such as the topic title). There are community conventions (sometimes loosely adhered to) for structuring and interest check or group buy post. For example, keyset names are often prefaced by one or more infocodes giving relevant information about the style and manufacturer of the keycaps (ex. "GMK BoW"). To extract relevant features from the unstructured fields, the project uses a parser using a grammar adapted to recognize keycap set-specific terminology. For example, the parser can extract infocodes and keyset titles from topic titles. Similar to data acquisition, data cleaning will occur separately for topic index data and topic page data.

### Data Processing/Cleaning Steps
1. Scrape data from topic indexes
2. Process topic index data
	- process structured data fields (topic id, creator, views, replies, etc.)
	- run topic titles through parser to detect keyset name, infocodes, product type (keyset or other)
3. Store topic index data in database
4. Scrape data from relevant topic pages
5. Process topic page data
	- process structured data (mostly this is the topic creation date)
	- clean first post data (separating and storing links)
	- aggregate post-level data (aggregating total posts, creator posts, time to X posts)
6. Update database with processed topic page data

Additionally, the data processing stage is planned to include linking group buy posts with any related interest check posts based on the posting user and/or keyset title.

---
## Data Analysis

This stage is planned to largely take place in Jupyter and will initially produce a one-off report (with nice graphs). As discussed in the extension section, any useful statistics found in exploratory data analysis may be later formalized into a dashboard.

**TEST PLAN (TBC)**

----
## Results and Visualizations

*TBC*

---
## Potential Extensions

- Classifieds board analysis (for post-group buy interest in sets)
- Further topic content analysis:
  - Number of kits per buy
  - Number/distribution of different vendors
- Other data sources (such as reddit)
- Automatic data intake and publishing:
  - Public dashboard/report
  - Automated intake and processing of data for dashboard
