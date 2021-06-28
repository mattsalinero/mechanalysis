/* SQL query for pulling per-infocode data */
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
