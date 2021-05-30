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
	board_id VARCHAR, --renamed from board
	board_accessed VARCHAR, --datetime value
	title VARCHAR,
	num_posts INTEGER,
	num_posters INTEGER,
	num_creator_posts INTEGER,
	post_25_delta VARCHAR, --time interval
	post_50_delta VARCHAR, --time interval
	topic_accessed VARCHAR --datetime value
	);

CREATE TABLE topic_icode (
	topic_id VARCHAR NOT NULL,
	info_code VARCHAR NOT NULL,
	PRIMARY KEY (topic_id, info_code),
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);

CREATE TABLE topic_link (
	id INTEGER PRIMARY KEY,
	topic_id VARCHAR NOT NULL,
	link VARCHAR NOT NULL,
	domain VARCHAR, --stores the top level domain
	FOREIGN KEY (topic_id) REFERENCES topic_data(topic_id)
	);
