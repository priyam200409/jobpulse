SELECT
    experience,
    COUNT(*) AS job_count
FROM postings
WHERE experience IS NOT NULL
  AND TRIM(experience) <> ''
GROUP BY experience
ORDER BY job_count DESC;