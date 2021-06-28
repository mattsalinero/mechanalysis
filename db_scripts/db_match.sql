/* SQL query for determining group buy-interest check matches */
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
