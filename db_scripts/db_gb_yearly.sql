/* SQL query for pulling yearly aggregate stats for keycap group buys */
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
