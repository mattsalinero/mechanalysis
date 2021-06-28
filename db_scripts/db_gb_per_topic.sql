/* SQL query for pulling per-topic group buy data for visualization */
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
