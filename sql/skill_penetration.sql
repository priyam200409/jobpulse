WITH total_jobs AS (
    SELECT COUNT(*) AS total_job_count
    FROM postings
)

SELECT
    s.skill_name,
    s.category,
    COUNT(DISTINCT sm.posting_id) AS job_count,
    ROUND(
        100.0 * COUNT(DISTINCT sm.posting_id)
        / total_jobs.total_job_count,
        2
    ) AS demand_percentage
FROM skills s
JOIN skill_mentions sm
    ON s.skill_id = sm.skill_id
CROSS JOIN total_jobs
GROUP BY
    s.skill_id,
    s.skill_name,
    s.category,
    total_jobs.total_job_count
ORDER BY
    demand_percentage DESC,
    s.skill_name;