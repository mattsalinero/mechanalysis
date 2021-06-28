/* SQL query for pulling per-domain data */
SELECT
    LOWER(domain) as domain,
    COUNT(DISTINCT topic_id) as num_topics,
    COUNT(id) as num_occurances
FROM topic_link
GROUP BY LOWER(domain)
ORDER BY num_topics desc;
