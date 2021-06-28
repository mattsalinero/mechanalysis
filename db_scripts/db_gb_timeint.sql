/* SQL query for pulling keycap group buy time interval stats
    - need to manually aggregate these in python
    - pulls topic level post_50_delta stats
    - sqlite doesn't support time intervals */
    SELECT
        topic_id,
        STRFTIME('%Y', topic_created) as gb_year,
        post_50_delta
    FROM topic_data
    WHERE product_type = 'keycaps'
            AND board_id = '70'
    ORDER BY gb_year;
