from dataclasses import dataclass
from typing import Optional


@dataclass
class JobPosting:
    posting_id: str
    job_title: str
    company: str
    location: str
    experience: Optional[str]
    description: str
    requirements: Optional[str]
    posted_date: Optional[str]
    source: str
    job_url: str
    scraped_at: str