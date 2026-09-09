SELECT
    location,
    COUNT(DISTINCT posting_id) AS job_count
FROM postings
GROUP BY
    location
ORDER BY
    job_count DESC,
    location ASC;