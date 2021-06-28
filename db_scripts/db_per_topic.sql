/* SQL query for pulling per-topic group buy & interest check data
    - omits no topic_created data, but includes interest check topics */
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
