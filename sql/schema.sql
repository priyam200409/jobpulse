PRAGMA foreign_keys = ON;

-- =========================================================
-- JOBPULSE DATABASE SCHEMA
-- =========================================================
--
-- Current market data:
--   postings
--   skills
--   skill_mentions
--
-- Operational metadata:
--   scrape_runs
--
-- Historical market data:
--   job_snapshots
--   snapshot_skill_mentions
--
-- Important:
-- Historical snapshot tables intentionally do NOT have
-- foreign keys back to the current postings table.
--
-- A job disappearing from the current market must not
-- delete its historical record.
-- =========================================================


-- =========================================================
-- CURRENT JOB POSTINGS
-- =========================================================

CREATE TABLE IF NOT EXISTS postings (
    posting_id TEXT PRIMARY KEY,
    job_title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    experience TEXT,
    description TEXT,
    requirements TEXT,
    posted_date DATE,
    source TEXT,
    job_url TEXT,
    scraped_at TIMESTAMP,
    salary_min REAL,
    salary_max REAL,
    employment_type TEXT,
    category TEXT
);


-- =========================================================
-- SKILL TAXONOMY
-- =========================================================

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);


-- =========================================================
-- CURRENT SKILL MENTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS skill_mentions (
    posting_id TEXT NOT NULL,
    skill_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0,

    PRIMARY KEY (
        posting_id,
        skill_id
    ),

    FOREIGN KEY (posting_id)
        REFERENCES postings(posting_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE
);


-- =========================================================
-- INGESTION / SCRAPE RUN HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS scrape_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    run_timestamp TIMESTAMP NOT NULL,
    records_collected INTEGER DEFAULT 0,
    records_new INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0
);


-- =========================================================
-- HISTORICAL JOB SNAPSHOTS
-- =========================================================
--
-- IMPORTANT:
-- No foreign key to postings.
--
-- A snapshot is an independent historical record.
-- =========================================================

CREATE TABLE IF NOT EXISTS job_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,

    posting_id TEXT NOT NULL,
    snapshot_date DATE NOT NULL,

    job_title TEXT,
    company TEXT,
    location TEXT,
    experience TEXT,
    posted_date DATE,
    source TEXT,
    salary_min REAL,
    salary_max REAL,
    employment_type TEXT,
    category TEXT,

    UNIQUE (
        snapshot_date,
        posting_id
    )
);


-- =========================================================
-- HISTORICAL SNAPSHOT SKILLS
-- =========================================================
--
-- IMPORTANT:
-- skill_name is stored directly rather than relying on
-- the current skill dictionary remaining unchanged.
--
-- This makes historical snapshots more resilient if the
-- taxonomy is later modified.
-- =========================================================

CREATE TABLE IF NOT EXISTS snapshot_skill_mentions (
    snapshot_id INTEGER NOT NULL,
    posting_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,

    PRIMARY KEY (
        snapshot_id,
        posting_id,
        skill_name
    ),

    FOREIGN KEY (snapshot_id)
        REFERENCES job_snapshots(snapshot_id)
        ON DELETE CASCADE
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_postings_source
ON postings(source);


CREATE INDEX IF NOT EXISTS idx_postings_posted_date
ON postings(posted_date);


CREATE INDEX IF NOT EXISTS idx_postings_company
ON postings(company);


CREATE INDEX IF NOT EXISTS idx_postings_location
ON postings(location);


CREATE INDEX IF NOT EXISTS idx_skill_mentions_skill
ON skill_mentions(skill_id);


CREATE INDEX IF NOT EXISTS idx_skill_mentions_posting
ON skill_mentions(posting_id);


CREATE INDEX IF NOT EXISTS idx_scrape_runs_source
ON scrape_runs(source);


CREATE INDEX IF NOT EXISTS idx_scrape_runs_timestamp
ON scrape_runs(run_timestamp);


CREATE INDEX IF NOT EXISTS idx_job_snapshots_date
ON job_snapshots(snapshot_date);


CREATE INDEX IF NOT EXISTS idx_job_snapshots_posting
ON job_snapshots(posting_id);


CREATE INDEX IF NOT EXISTS idx_snapshot_skill_mentions_snapshot
ON snapshot_skill_mentions(snapshot_id);


CREATE INDEX IF NOT EXISTS idx_snapshot_skill_mentions_skill
ON snapshot_skill_mentions(skill_name);