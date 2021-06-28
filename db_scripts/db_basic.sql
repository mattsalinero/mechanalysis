/* SQL query for pulling basic aggregate stats */
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
