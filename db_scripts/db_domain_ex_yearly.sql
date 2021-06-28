/* SQL query for pulling expanded yearly domain/vendor data 
    - detection of discord expanded to include other formats of discord links*/
SELECT
    CASE
        WHEN link LIKE '%discord%' THEN 'discord.gg'
        WHEN LOWER(domain) LIKE ('%' || REPLACE(LOWER(set_name), ' ', '') || '%')
            THEN 'custom domain'
        ELSE LOWER(domain)
    END as domain_type,
    STRFTIME('%Y', tdata.topic_created) as gb_year,
    COUNT(DISTINCT ldata.topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link as ldata
JOIN topic_data as tdata
    ON ldata.topic_id = tdata.topic_id
GROUP BY domain_type, gb_year
ORDER BY gb_year;
