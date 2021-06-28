/* SQL query for pulling per-topic infocode data (separate rows for secondary icodes) */
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
