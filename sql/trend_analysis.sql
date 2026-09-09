WITH weekly_jobs AS (
    SELECT
        strftime('%Y-%W', snapshot_date) AS week,
        COUNT(DISTINCT posting_id) AS job_count
    FROM job_snapshots
    GROUP BY strftime('%Y-%W', snapshot_date)
),

weekly_with_previous AS (
    SELECT
        week,
        job_count,
        LAG(job_count) OVER (
            ORDER BY week
        ) AS previous_week_jobs
    FROM weekly_jobs
)

SELECT
    week,
    job_count,
    previous_week_jobs,
    CASE
        WHEN previous_week_jobs IS NULL THEN NULL
        WHEN previous_week_jobs = 0 THEN NULL
        ELSE ROUND(
            100.0 * (job_count - previous_week_jobs)
            / previous_week_jobs,
            2
        )
    END AS wow_change_percentage
FROM weekly_with_previous
ORDER BY week;