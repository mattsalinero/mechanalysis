/* SQL query for pulling categorical icode data by year */
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
