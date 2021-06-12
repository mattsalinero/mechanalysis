# Mechanical  Keyboard Analysis Project

Creator: Matt Salinero

Created: 2021-01-11

Last Updated: 2021-06-09

---
## Project Overview

*TBC*

---
## Task

This project will attempt to analyze data on keycap group buys listed on community websites to identify year over year trends.

### Context
Over the last \~five years a community of mechanical keyboard enthusiasts has experienced rapid growth. Being a mechanical keyboard enthusiast involves researching, preordering, waiting for, and assembling exclusive mechanical keyboards from limited run keyboard components (such as keycaps, keyboard chassis, and switches). Also, mechanical keyboards can be typed on! 

At present, the market for enthusiast-level mechanical keyboard components is fragmented and largely lacks major consolidation or corporate investment. Instead, the manufacture of components is often financed using a group buy system that relies on the community preordering components to cover manufacturing costs. These group buys are often advertised on dedicated community forums, subreddits, and content creator communities dedicated to mechanical keyboards. 

However, despite group buys being publicly advertised, aggregated data on group buy sucess, failure, or popularity is not readily accessible. Much of the available information on group buys is buried in unstructured forum threads or posts. Clear trends present in the publically available data could be used by aspiring component designers to inform their choices when attempting to realize their own keycap set.

#### Terminology 
- group buy: a form of crowdfunding in which user pre-orders are used to fund manufacturing 
- interest check: a pre-group buy advertisement of a potential group buy product (used to gauge viability of group buy)
- keycap: a keyboard component, the (usually) molded plastic key your fingers make contact with to type
- keycap profile: the shape of the keycaps
- keycap material: the material a keycap is made out of
- keycap manufacturer: the factory or company producing the keycaps
- infocode: a short abbreviation containing keycap profile, material, or manufacturer information
- keyset: a specific set of keycaps offered for sale, commonly include unique colors and/or design elements
- post (forum): the base unit of communication on a forum, a message submitted by a user
- topic (forum): a discussion thread on a forum, includes one or more posts (including original post by the topic creator)
- topic index (forum): a navigation page including basic details for many topics (e.g. title), usually in reverse chronological order
- topic page (forum): a page associated with a single topic, including topic content (e.g. individual posts)

### Project Goals
Analysis in this project will focus on determining:
- how many keysets have been released/advertised
- corresponding keyset names and infocodes
- date of group buy for each keyset
- interest metrics for each keyset (such as topic replies and views)
- statistical link (if any) between popularity of group buy and popularity of interest check for each keyset

### Out of Scope
Analysis of prebuilt keyboards and keyboard components other than keycaps (ex. switches, keyboard chassis) isn't a part of this project, though potentially the project could eventually be extended to look at those items.

---
## Data Sources

The main data source for this project is publicly available data from [geekhack.org](https://geekhack.org/), a community forum for mechanical keyboards. Relevant data will be acquired by scraping public topic post content and topic metadata from geekhack's "group buys and preorders" and "interest checks" forums. As the project is focused on the effects/outcomes of activities on these community forums, acquiring the available data straight from this source provides the best chance of capturing relevant information. The webscraper will use the "beautifulsoup4" and "requests" python libraries to extract and save scraped data for analysis.

To minimize requests to geekhack, scraping will be performed in two stages. First, the scraper will ingest topic titles from group buy/interest check topic index pages and perform initial data processing to identify relevant topics (about keysets). In the second stage, the scraper will access the topic pages for the topics identified in stage one to extract additional data about each relevant topic.

## Data Storage

Collected data will be stored in either files (in the case of raw data for archive) or a database (for processed/cleaned data)

### Raw Data Files
The raw scraped data from topic indexes will be aggregated and stored in .csv files per board scraped. Scraped topic page data will be stored in .json files for each scraped topic.

### Database
A database will be used to store cleaned and processed data. As this project is only focused on keysets (for the moment), any cleaned data on non-keyset topics (such as data gathered from topic index pages) will be stored. These database entries may be incomplete as no topic page-level data gathering is planned for non-keyset topics. The current database schema is included below.

#### Database Choice (SQLite)
SQLite was chosen to store the final dataset out of all the possible options (spreadsheets, .csv files, full fledged relational dbs, etc.) for a variety of reasons. This project involves a fairly low number of records (~5000 in the main table) and a relatively simple schema using 3 tables. This volume of data would be possible to store in a spreadsheet or series of .csv files, but a relational database would make sythesizing data from multiple tables easier when analyzing and visualizing. Due to the low performance demands on the database SQLite was the convenient choice (as it doesn't need a separate server instance).

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
1. scrape data from topic indexes
2. process topic index data (from both group buy and interest check forums)
	- process structured data fields (topic id, creator, views, replies, etc.)
	- run topic titles through parser to detect keyset name, infocodes, product type (keyset or other)
3. store topic index data in database
4. scrape data from relevant topic pages
5. process topic page data
	- process structured data (mostly this is topic creation date)
	- clean first post data (separating and storing links and domains)
    	- links are separated from image sources, then parsed using a library to extract just the domain names
	- aggregate post-level data from first 50 posts in topic (number of creator posts, time to X posts in topic)
6. update database with processed topic page data
7. manually clean/validate database
	- scan through topic_data correcting improperly parsed set names
	- manually remove indications of "round 2" or similar

### Topic Title Parsing
This project uses Lark's implementation of an Earley parser and a custom grammar that recognizes the infocodes and general structure of group buy topics. The grammar tries to identify the section of the topic title where the keyset is identified (usually of the form `[infocode][setname]`) by referencing a dictionary of possible infocodes that are currently in use. There is a finite (but growing) number of infocodes currently in use and the parser can use an identified infocode to find the (usually adjacent) name of the keyset.

The full parser grammar (including the dictionary of infocodes) is stored in a [.lark file](title_gram.lark).

---
## Data Analysis

The initial analysis for this project examined the cleaned data over a number of analysis dimensions. During the analysis, each dimension was compared against one or more other dimensions to identify correlations or other trends that may explain the current state of the group buy scene for mechanical keyboard components.

#### Analysis Dimensions:
  - group buy topic creation date
  - group buy and interest check infocodes
  - group buy popularity/hype
  - linked domains in group buys 
    - potentially shows number of regional vendors used for fulfillment
    - includes data on other discussion platforms (discord)
  - matches between a group buy and a corresponding interest check (a "gb-ic match")
  - multiple group buy rounds for the same product

To perform the analysis, SQL queries slicing the data to isolate two or more dimensions were run on the database containing the previously cleaned data. Some of these queries (largely created on an ad-hoc basis) are available in this [analysis query script](db_scripts/db_analysis.sql). The final project presentation/report contains visualizations based on some of the queries generated at this stage.

### Group Buy Hype Measurement
Measuring the sucess of a group buy is an important piece of this analysis, however, sales data (and other data on the financial status of each group buy) was not readily available. Instead, this project uses group buy popularity (in the form of user engagement) as the main success metric for analysis. However, the simplest engagement metrics (raw topic views/replies) are biased against newer group buys and therefore aren't reliable when comparing group buy data across different years. Many group buys continue accumulating views and replies long after the group buy has ended (for example, when the product finally begins shipping or extras are later sold).

#### The Hype Metric
This project uses a "hype" metric, which tracks user engagement with the group buy (in the form of posting responses) near the time the group buy topic was created. The hype metric is binary, where a topic is considered "hyped" if it reaches 50 posts in the first 30 days, and not hyped if it fails to do so.

- limiting analysis to just the first 30 days mitigates the bias against newer topics
- the target 50th post is still on the first topic page
    - no additional page requests needed to calculate this metric
- 30 days/1 month is a common length of time for a group buy to be open
  - also tested 14 and 21 days, but 30 seemed like the natural choice
- using a binary metric reduces the effect of large outliers in the dataset

#### Implementation Challenges
- each post contains a timestamp that can be compared to the topic's creation timestamp
    - no similar information available for views
- SQLite doesn't support time intervals/calculations using time intervals
  - data for the group buy hype was stored as a string and parsed and aggregated separately during analysis

### Group Buy - Interest Check Topic Matching
The analysis at this stage included matching group buy topics to corresponding interest check topics. Gb-ic matches can help determine what percentage of interest checks result in a group buy or how strongly an interest check's popularity is correlated with the existence (or popularity) of a corresponding group buy. 
  
#### Assumptions
- keysets have a consistent (and unique) name across group buy and interest check topics
- `topic_id` is assigned by the forum sequentially (i.e. earlier topics have lower topic ids)
- an interest check topic is made before the corresponding group buy topic
- when multiple group buys are run for the same product, they are run sequentially (e.g. a "round 2" group buy)

#### Matching Algorithm
- retreive `topic_id`, `set_name`, and `info_code` data for each topic to match
  - the combination of `info_code` and `set_name` is the `full_name` for the keyset
- calculate the "topic rank" for each topic
  - topic rank reflects how many previous topics were created with the same name
  - for example, `topic_rank: 1` is the first topic with that name and `topic_rank: 5` is the fifth
  - calculated by comparing `topic_id` for each topic against all other topics with the same `full_name` (case insensitive)
    - lowest `topic_id` is rank 1, next lowest is rank 2, and so on
    - in SQL this is implemented using a window function to `PARTITION BY full_name` and `ORDER BY topic_id`
- match topics based on name and `topic_rank`
  - for a successful interest check, the next topic created with that name should be a group buy
  - in SQL this is implemented by checking if `gb.topic_rank = ic.topic_rank + 1` for any potential match

#### GB-IC matching query:
```sql
WITH --cte to get base view with full_name and data relevant for matching
    full_data (topic_id, board, info_code, set_name, full_name, topic_rank)
    AS (
        SELECT
            tdata.topic_id,
            CASE
                WHEN tdata.board_id = '70' THEN 'gb'
                WHEN tdata.board_id = '132' THEN 'ic'
            END as board,
            icode.info_code,
            set_name,
            icode.info_code || ' ' || set_name as full_name,
            ROW_NUMBER() OVER( 
                PARTITION BY info_code, UPPER(set_name) 
                ORDER BY CAST(tdata.topic_id as INT)
                ) as topic_rank --lists if first, second etc. gb/ic
        FROM topic_data as tdata
        JOIN (
            SELECT --pulls first/primary infocode only
                topic_id,
                info_code,
                ROW_NUMBER() OVER(PARTITION BY topic_id) as row_num
            FROM topic_icode
            ) icode
            ON tdata.topic_id = icode.topic_id
                AND icode.row_num = 1
        WHERE product_type = 'keycaps'
    )
SELECT
    gbdata.topic_id as gb_topic_id,
    icdata.topic_id as ic_topic_id,
    IFNULL(gbdata.full_name, icdata.full_name) as full_name,
    gbdata.topic_rank,
    CAST(IFNULL(gbdata.topic_id, icdata.topic_id) as INT) as order_calc
FROM (
    SELECT *
    FROM full_data
    WHERE board = 'gb'
    ) gbdata
OUTER JOIN ( --result includes all topics
    SELECT *
    FROM full_data
    WHERE board = 'ic'
    ) icdata
    ON gbdata.full_name = icdata.full_name --checks name, topic_rank for matches
        AND gbdata.topic_rank = (icdata.topic_rank + 1)
ORDER BY order_calc;
```

----
## Results and Visualizations

*TBC*
- overall story increased saturation in the market?
- shift away from group buys to instock/greater availability?
- lately, increased diversification in different profiles/manufacturers

### Key Takeaways

*TBC*

---
## Potential Extensions

- classifieds board analysis (for post-group buy interest in sets)
- further topic content analysis:
  - number of kits per buy
  - number/distribution of different vendors
  - sentiment analysis of first page posts
- other data sources (such as reddit)
- automatic data intake and publishing:
  - public dashboard/report
  - automated intake and processing of data for dashboard
