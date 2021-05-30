CREATE TABLE topic_data (
	topic_id VARCHAR PRIMARY KEY,
	product_type VARCHAR,
	thread_type VARCHAR,
	set_name VARCHAR,
	creator VARCHAR,
	creator_id VARCHAR,
	views INTEGER,
	replies INTEGER,
	board VARCHAR,
	board_accessed VARCHAR, --datetime value
	title VARCHAR
	);

CREATE TABLE topic_icode (
	topic_id VARCHAR NOT NULL,
	info_code VARCHAR NOT NULL,
	PRIMARY KEY (topic_id, info_code),
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);

CREATE TABLE topic_advanced (
	topic_id VARCHAR PRIMARY KEY,
	topic_created VARCHAR, --datetime value
	num_posts INTEGER,
	num_posters INTEGER,
	num_creator_posts INTEGER,
	percent_creator_posts REAL,
	post_25_delta VARCHAR, --time interval
	post_50_delta VARCHAR, --time interval
	topic_accessed VARCHAR, --datetime value
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);

CREATE TABLE topic_link (
	id INTEGER PRIMARY KEY,
	topic_id VARCHAR NOT NULL,
	link VARCHAR NOT NULL,
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);
