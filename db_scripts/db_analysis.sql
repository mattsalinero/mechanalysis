/* analysis SQL queries for mech analysis project */

/* basic stats query */
SELECT
    CASE
        WHEN board_id = '70' THEN 'keycap group buy'
        WHEN board_id = '132' THEN 'keycap interest check'
    END as 'topic type',
    COUNT(topic_id) as 'num topics',
    CAST(AVG(views) as INT) as 'average topic views',
    CAST(AVG(replies) as INT) as 'average topic replies',
    CAST(SUM(views) as INT) as 'total topic views',
    CAST(SUM(replies) as INT) as 'total topic replies'
FROM topic_data
WHERE product_type = 'keycaps'
GROUP BY board_id
UNION
SELECT
    CASE
        WHEN board_id = '70' THEN 'generic group buy'
        WHEN board_id = '132' THEN 'generic interest check'
    END as 'topic type',
    COUNT(topic_id) as 'num topics',
    CAST(AVG(views) as INT) as 'average topic views',
    CAST(AVG(replies) as INT) as 'average topic replies',
    CAST(SUM(views) as INT) as 'total topic views',
    CAST(SUM(replies) as INT) as 'total topic replies'
FROM topic_data
GROUP BY board_id;

/* per-topic group buy data for visualization */
SELECT
    tdata.topic_id,
    icode.info_code,
    set_name,
    icode.info_code || ' ' || set_name as 'full_name',
    creator,
    DATETIME(topic_created) as 'topic_created',
    views,
    replies,
    num_posters,
    (num_creator_posts * 1.0 / num_posts) * 100 as 'percent_creator_posts',   
    DATETIME(post_25_delta) as 'post_25_delta', --currently broken (many missing values)
    DATETIME(post_50_delta) as 'post_50_delta' --currently broken (many missing values)
FROM topic_data as tdata
JOIN (
    SELECT --window function to only pull first/primary infocode (no duplicate topic ids)
        topic_id,
        info_code,
        ROW_NUMBER() OVER(PARTITION BY topic_id) as row_num
    FROM topic_icode
    ) icode
    ON tdata.topic_id = icode.topic_id
        AND icode.row_num = 1
WHERE product_type = 'keycaps'
    AND board_id = '70'
ORDER BY DATETIME(topic_created) desc;

/* per-topic group buy + interest check data (no topic_created, but includes ics) */
SELECT
    tdata.topic_id,
    CASE
        WHEN board_id = '70' THEN 'gb'
        WHEN board_id = '132' THEN 'ic'
    END as 'board',
    icode.info_code,
    set_name,
    icode.info_code || ' ' || set_name as 'full_name',
    creator,
    views,
    replies
FROM topic_data as tdata
JOIN (
    SELECT --window function to only pull first/primary infocode (no duplicate topic ids)
        topic_id,
        info_code,
        ROW_NUMBER() OVER(PARTITION BY topic_id) as row_num
    FROM topic_icode
    ) icode
    ON tdata.topic_id = icode.topic_id
        AND icode.row_num = 1
WHERE product_type = 'keycaps'
ORDER BY CAST(tdata.topic_id as INT) desc;

/* per-infocode data */
SELECT
    info_code,
    CASE
        WHEN tdata.board_id = '70' THEN 'gb'
        WHEN tdata.board_id = '132' THEN 'ic'
    END as 'board',
    COUNT(info_code),
    CAST(AVG(tdata.views) as INT) as 'average_views',
    MAX(tdata.views) as 'max_views',
    CAST(AVG(tdata.replies) as INT) as 'average_replies',
    MAX(tdata.replies) as 'max_replies'
FROM topic_icode as icode
JOIN topic_data as tdata
    ON icode.topic_id = tdata.topic_id
GROUP BY info_code, board
ORDER BY COUNT(info_code) desc;

/* infocodes over time (include duplicate infocodes) */

--TBC

/* top links/vendors */

--TBC 

/* group buy interest check match */

--TBC

/* success metrics (limit to last two years and try to correlate low replies/views with certain characteristics) */
