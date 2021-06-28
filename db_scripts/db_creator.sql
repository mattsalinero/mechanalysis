/* SQL query for pulling per-creator data */
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
