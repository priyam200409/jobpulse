SELECT
    s.skill_name AS skill,
    s.category,
    COUNT(DISTINCT sm.posting_id) AS job_count
FROM skill_mentions sm
JOIN skills s
    ON sm.skill_id = s.skill_id
GROUP BY
    s.skill_id,
    s.skill_name,
    s.category
ORDER BY
    job_count DESC,
    skill ASC;