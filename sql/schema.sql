PRAGMA foreign_keys = ON;

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

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_mentions (
    posting_id TEXT NOT NULL,
    skill_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0,

    PRIMARY KEY (posting_id, skill_id),

    FOREIGN KEY (posting_id)
        REFERENCES postings(posting_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scrape_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    run_timestamp TIMESTAMP NOT NULL,
    records_collected INTEGER DEFAULT 0,
    records_new INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0
);
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
    FOREIGN KEY (posting_id)
        REFERENCES postings(posting_id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS snapshot_skill_mentions (
    snapshot_id INTEGER NOT NULL,
    posting_id TEXT NOT NULL,
    skill_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0,

    PRIMARY KEY (
        snapshot_id,
        posting_id,
        skill_id
    ),

    FOREIGN KEY (snapshot_id)
        REFERENCES job_snapshots(snapshot_id)
        ON DELETE CASCADE,

    FOREIGN KEY (posting_id)
        REFERENCES postings(posting_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE
);