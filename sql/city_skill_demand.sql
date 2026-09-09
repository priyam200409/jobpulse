SELECT
    p.location,
    s.skill_name,
    COUNT(DISTINCT p.posting_id) AS job_count
FROM postings p
JOIN skill_mentions sm
    ON p.posting_id = sm.posting_id
JOIN skills s
    ON sm.skill_id = s.skill_id
GROUP BY
    p.location,
    s.skill_name
ORDER BY
    p.location,
    job_count DESC;