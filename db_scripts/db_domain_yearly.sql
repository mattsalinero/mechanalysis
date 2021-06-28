/* SQL query for pulling yearly domain data */
SELECT
    LOWER(domain) as domain,
    STRFTIME('%Y', tdata.topic_created) as gb_year,
    COUNT(DISTINCT ldata.topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link as ldata
JOIN topic_data as tdata
    ON ldata.topic_id = tdata.topic_id
GROUP BY LOWER(domain), gb_year
ORDER BY gb_year;
