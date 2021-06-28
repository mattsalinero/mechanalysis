/* SQL query for pulling yearly icode data */
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
