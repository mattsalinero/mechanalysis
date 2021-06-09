/* analysis SQL queries for mech analysis project */

/* basic aggregate stats */
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

/* keycap group buy yearly aggregate stats */
SELECT
    ydata.*,
    num_icodes
FROM (
    SELECT --this derived table calculates most rows
        STRFTIME('%Y', topic_created) as gb_year,
        COUNT(tdata.topic_id) as num_gbs,
        COUNT(DISTINCT creator_id) as num_creators,
        CAST(AVG(views) as INT) as avg_views,
        MAX(views) as max_views,
        SUM(views) as sum_views,
        CAST(AVG(replies) as INT) as avg_replies,
        MAX(replies) as max_replies,
        SUM(replies) as sum_replies,
        COUNT(CASE WHEN num_posts >= 25 THEN 1 END) * 100.0 
            / COUNT(tdata.topic_id) as percent_25_posts,
        COUNT(CASE WHEN num_posts >= 50 THEN 1 END) * 100.0 
            / COUNT(tdata.topic_id) as percent_50_posts,
        AVG(IFNULL(ldata.num_links, 0)) as avg_links
    --average time for gbs reaching 25/50 posts
    FROM topic_data as tdata
    LEFT JOIN (
        SELECT
            topic_id,
            COUNT(id) as num_links
        FROM topic_link
        GROUP BY topic_id
        ) ldata
    ON tdata.topic_id = ldata.topic_id
    WHERE product_type = 'keycaps'
        AND board_id = '70'
    GROUP BY gb_year
    ) ydata
JOIN (
    SELECT --this derived table calculates number of infocodes used
        STRFTIME('%Y', topic_created) as gb_year,
        COUNT(DISTINCT icode.info_code) as num_icodes
    FROM topic_data as itdata
    JOIN topic_icode as icode
        ON itdata.topic_id = icode.topic_id
    WHERE product_type = 'keycaps'
        AND board_id = '70'
    GROUP BY gb_year
    ) iydata
ON ydata.gb_year = iydata.gb_year
ORDER BY gb_year;

/* keycap group buy time interval stats (aggregate in python)
    - pulls topic level post_50_delta stats
    - sqlite doesn't support time intervals */
    SELECT
        topic_id,
        STRFTIME('%Y', topic_created) as gb_year,
        post_50_delta
    FROM topic_data
    WHERE product_type = 'keycaps'
            AND board_id = '70'
    ORDER BY gb_year

/* per-topic group buy data for visualization */
SELECT
    tdata.topic_id,
    icode.info_code,
    set_name,
    icode.info_code || ' ' || set_name as full_name,
    creator,
    DATETIME(topic_created) as topic_created,
    IFNULL(ldata.num_links, 0) as num_links,
    views,
    replies,
    num_posters,
    (num_creator_posts * 1.0 / num_posts) * 100 as percent_creator_posts,   
    DATETIME(post_25_delta) as post_25_delta,
    DATETIME(post_50_delta) as post_50_delta
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
LEFT JOIN (
    SELECT --aggregates total number of links in post
        topic_id,
        COUNT(link) as num_links
    FROM topic_link
    GROUP BY topic_id
    ) ldata
    ON tdata.topic_id = ldata.topic_id
WHERE product_type = 'keycaps'
    AND board_id = '70'
ORDER BY DATETIME(topic_created) desc;

/* per-topic group buy + interest check data (no topic_created, but includes ics) */
SELECT
    tdata.topic_id,
    CASE
        WHEN board_id = '70' THEN 'gb'
        WHEN board_id = '132' THEN 'ic'
    END as board,
    icode.info_code,
    set_name,
    icode.info_code || ' ' || set_name as full_name,
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

/* per-topic infocode data (separate rows for secondary infocodes) */
SELECT
    tdata.topic_id,
    icode.info_code,
    set_name,
    creator,
    DATETIME(topic_created) as topic_created,
    views,
    replies,
    num_posters,
    (num_creator_posts * 1.0 / num_posts) * 100 as percent_creator_posts,   
    DATETIME(post_25_delta) as post_25_delta,
    DATETIME(post_50_delta) as post_50_delta
FROM topic_data as tdata
JOIN topic_icode as icode
    ON tdata.topic_id = icode.topic_id
WHERE product_type = 'keycaps'
    AND board_id = '70'
ORDER BY DATETIME(topic_created) desc;

/* per-infocode data */
SELECT
    info_code,
    CASE
        WHEN tdata.board_id = '70' THEN 'gb'
        WHEN tdata.board_id = '132' THEN 'ic'
    END as board,
    COUNT(info_code) as occurances,
    CAST(AVG(tdata.views) as INT) as average_views,
    MAX(tdata.views) as max_views,
    CAST(AVG(tdata.replies) as INT) as average_replies,
    MAX(tdata.replies) as max_replies
FROM topic_icode as icode
JOIN topic_data as tdata
    ON icode.topic_id = tdata.topic_id
GROUP BY info_code, board
ORDER BY COUNT(info_code) desc;

/* yearly icode data */
SELECT
    info_code,
    STRFTIME('%Y', tdata.topic_created) as gb_year,
    COUNT(info_code) as occurances,
    CAST(AVG(tdata.views) as INT) as average_views,
    MAX(tdata.views) as max_views,
    CAST(AVG(tdata.replies) as INT) as average_replies,
    MAX(tdata.replies) as max_replies
FROM topic_icode as icode
JOIN topic_data as tdata
    ON icode.topic_id = tdata.topic_id
WHERE board_id = '70'
GROUP BY info_code, gb_year
ORDER BY gb_year;

/* categorical yearly icode data */
WITH cat_icode (topic_id, cat, info_code, topic_created) as (
    SELECT
        icode.topic_id as topic_id,
        CASE
            WHEN icode.info_code = 'GMK'
                THEN 'GMK'
            WHEN icode.info_code in ('PBT', 'EPBT', 'IFK', 'CRP', 'GA')
                THEN 'PBT'
            WHEN icode.info_code in ('JTK', 'DCS', 'TH')
                THEN 'ABS'
            WHEN icode.info_code in ('MG', 'SA', 'SP', 'HSA', 'KAT', 'KAM',
                'DSA', 'MDA', 'XDA')
                THEN 'alternative'
            ELSE 'other'
        END as cat,
        icode.info_code as info_code,
        tdata.topic_created as topic_created
    FROM topic_icode as icode
    JOIN topic_data as tdata
        ON icode.topic_id = tdata.topic_id
    WHERE board_id = '70'
    )
SELECT
    cat,
    STRFTIME('%Y', topic_created) as gb_year,
    COUNT(DISTINCT topic_id) as occurances
FROM cat_icode
GROUP BY cat, gb_year
ORDER BY gb_year;

/* per-domain/vendor data */
SELECT
    LOWER(domain) as domain,
    COUNT(DISTINCT topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link
GROUP BY LOWER(domain)
ORDER BY num_topics desc;

/* yearly domain data */
SELECT
    LOWER(domain) as domain,
    STRFTIME('%Y', tdata.topic_created) as gb_year,
    COUNT(DISTINCT ldata.topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link as ldata
JOIN topic_data as tdata
    ON ldata.topic_id = tdata.topic_id
GROUP BY LOWER(domain), gb_year
ORDER BY gb_year;

/* expanded domain/vendor data */
SELECT
    CASE
        WHEN link LIKE '%discord%' THEN 'discord.gg'
        WHEN LOWER(domain) LIKE ('%' || REPLACE(LOWER(set_name), ' ', '') || '%')
            THEN 'custom domain'
        ELSE LOWER(domain)
    END as domain_type,
    COUNT(DISTINCT ldata.topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link as ldata
JOIN topic_data as tdata
    ON ldata.topic_id = tdata.topic_id
GROUP BY domain_type
ORDER BY num_topics desc;

/* yearly expanded domain/vendor data */
SELECT
    CASE
        WHEN link LIKE '%discord%' THEN 'discord.gg'
        WHEN LOWER(domain) LIKE ('%' || REPLACE(LOWER(set_name), ' ', '') || '%')
            THEN 'custom domain'
        ELSE LOWER(domain)
    END as domain_type,
    STRFTIME('%Y', tdata.topic_created) as gb_year,
    COUNT(DISTINCT ldata.topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link as ldata
JOIN topic_data as tdata
    ON ldata.topic_id = tdata.topic_id
GROUP BY domain_type, gb_year
ORDER BY gb_year;

/* per-creator data */
SELECT
    creator_id,
    creator,
    COUNT(topic_id) as topics_created,
    COUNT(CASE WHEN board_id = '70' THEN 1 END) as gbs_created,
    COUNT(CASE WHEN board_id = '132' THEN 1 END) as ics_created,
    CAST(AVG(tdata.views) as INT) as average_views,
    CAST(AVG(tdata.replies) as INT) as average_replies
FROM topic_data as tdata
WHERE product_type = 'keycaps'
GROUP BY creator_id
ORDER BY topics_created desc;

/* group buy interest check match only */
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
LEFT JOIN ( --sqlite doesn't support FULL OUTER JOIN
    SELECT *
    FROM full_data
    WHERE board = 'ic'
    ) icdata
    ON gbdata.full_name = icdata.full_name
        AND gbdata.topic_rank = (icdata.topic_rank + 1)
UNION --approximate FULL OUTER JOIN using UNION
SELECT
    gbdata.topic_id as gb_topic_id,
    icdata.topic_id as ic_topic_id,
    IFNULL(gbdata.full_name, icdata.full_name) as full_name,
    gbdata.topic_rank,
    CAST(IFNULL(gbdata.topic_id, icdata.topic_id) as INT) as order_calc
FROM (
    SELECT *
    FROM full_data
    WHERE board = 'ic'
    ) icdata
LEFT JOIN ( --reversed positions of gb and ic tables
    SELECT *
    FROM full_data
    WHERE board = 'gb'
    ) gbdata
    ON gbdata.full_name = icdata.full_name
        AND gbdata.topic_rank = (icdata.topic_rank + 1)
ORDER BY order_calc;

/* group buy interest check match data */
WITH --cte to get base view with full_name and data relevant for matching
    full_data (
        topic_id, 
        board, 
        info_code, 
        set_name, 
        full_name, 
        creator,
        creator_id, 
        topic_created, 
        num_links, 
        views, 
        replies, 
        topic_rank
        )
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
            creator,
            creator_id,
            DATETIME(topic_created) as topic_created,
            IFNULL(ldata.num_links, 0) as num_links,
            views,
            replies,
            ROW_NUMBER() OVER( 
                PARTITION BY info_code, UPPER(set_name) 
                ORDER BY CAST(tdata.topic_id as INT)
                ) as topic_rank --lists if first, second etc. gb/ic
        FROM topic_data as tdata
        JOIN (
            SELECT --pulls first/primary infocode
                topic_id,
                info_code,
                ROW_NUMBER() OVER(PARTITION BY topic_id) as row_num
            FROM topic_icode
            ) icode
            ON tdata.topic_id = icode.topic_id
                AND icode.row_num = 1
        LEFT JOIN (
            SELECT --aggregates total number of links in post
                topic_id,
                COUNT(link) as num_links
            FROM topic_link
            GROUP BY topic_id
            ) ldata
            ON tdata.topic_id = ldata.topic_id
        WHERE product_type = 'keycaps'
    )
SELECT
    gbdata.topic_id as gb_topic_id,
    icdata.topic_id as ic_topic_id,
    IFNULL(gbdata.full_name, icdata.full_name) as full_name,
    IFNULL(gbdata.creator, icdata.creator) as creator,
    gbdata.topic_created,
    gbdata.num_links,
    gbdata.views as gb_views,
    icdata.views as ic_views,
    gbdata.replies as gb_replies,
    icdata.replies as ic_replies,
    gbdata.topic_rank,
    CAST(IFNULL(gbdata.topic_id, icdata.topic_id) as INT) as order_calc
FROM (
    SELECT *
    FROM full_data
    WHERE board = 'gb'
    ) gbdata
LEFT JOIN ( --sqlite doesn't support FULL OUTER JOIN
    SELECT *
    FROM full_data
    WHERE board = 'ic'
    ) icdata
    ON gbdata.full_name = icdata.full_name
        AND gbdata.topic_rank = (icdata.topic_rank + 1)
UNION --approximate FULL OUTER JOIN using UNION
SELECT
    gbdata.topic_id as gb_topic_id,
    icdata.topic_id as ic_topic_id,
    IFNULL(gbdata.full_name, icdata.full_name) as full_name,
    IFNULL(gbdata.creator, icdata.creator) as creator,
    gbdata.topic_created,
    gbdata.num_links,
    gbdata.views as gb_views,
    icdata.views as ic_views,
    gbdata.replies as gb_replies,
    icdata.replies as ic_replies,
    gbdata.topic_rank,
    CAST(IFNULL(gbdata.topic_id, icdata.topic_id) as INT) as order_calc
FROM (
    SELECT *
    FROM full_data
    WHERE board = 'ic'
    ) icdata
LEFT JOIN ( --reversed positions of gb and ic tables
    SELECT *
    FROM full_data
    WHERE board = 'gb'
    ) gbdata
    ON gbdata.full_name = icdata.full_name
        AND gbdata.topic_rank = (icdata.topic_rank + 1)
ORDER BY order_calc;
