WITH total_jobs AS (
    SELECT COUNT(*) AS total
    FROM postings
),

skill_jobs AS (
    SELECT
        s.skill_id,
        s.skill_name,
        s.category,
        COUNT(DISTINCT sm.posting_id) AS job_count
    FROM skill_mentions sm
    JOIN skills s
        ON sm.skill_id = s.skill_id
    GROUP BY
        s.skill_id,
        s.skill_name,
        s.category
)

SELECT
    skill_name AS skill,
    category,
    job_count,
    total_jobs.total AS total_jobs,
    ROUND(
        100.0 * job_count / total_jobs.total,
        2
    ) AS penetration_percentage
FROM skill_jobs
CROSS JOIN total_jobs
ORDER BY
    penetration_percentage DESC,
    skill ASC;