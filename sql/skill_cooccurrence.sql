SELECT
    s1.skill_name AS skill_1,
    s2.skill_name AS skill_2,
    COUNT(DISTINCT sm1.posting_id) AS job_count
FROM skill_mentions sm1
JOIN skill_mentions sm2
    ON sm1.posting_id = sm2.posting_id
    AND sm1.skill_id < sm2.skill_id
JOIN skills s1
    ON sm1.skill_id = s1.skill_id
JOIN skills s2
    ON sm2.skill_id = s2.skill_id
GROUP BY
    s1.skill_id,
    s2.skill_id,
    s1.skill_name,
    s2.skill_name
ORDER BY
    job_count DESC,
    skill_1 ASC,
    skill_2 ASC;