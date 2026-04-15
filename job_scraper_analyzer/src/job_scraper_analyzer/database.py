"""SQLite database layer with CRUD operations for job scraping and analysis."""

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from job_scraper_analyzer.models import Job


# SQL Statements for table creation
CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_url TEXT UNIQUE NOT NULL,
    site TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    is_remote BOOLEAN,
    job_type TEXT,
    description TEXT,
    min_salary REAL,
    max_salary REAL,
    salary_currency TEXT DEFAULT 'USD',
    salary_interval TEXT,
    date_posted DATE,
    job_level TEXT,
    company_industry TEXT,
    fit_rating INTEGER,
    status TEXT DEFAULT 'new',
    search_id INTEGER,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(id)
);
"""

CREATE_SEARCHES_TABLE = """
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_term TEXT NOT NULL,
    location TEXT,
    is_remote BOOLEAN,
    hours_old INTEGER,
    job_type TEXT,
    site_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ANALYSES_TABLE = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    batch_id TEXT,
    fit_rating INTEGER,
    justification TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
"""

# Index creation statements
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_site ON jobs(site);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_fit_rating ON jobs(fit_rating);",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_url ON jobs(job_url);",
]


def init_db(db_path: Path) -> None:
    """Initialize the database with required tables and indexes.
    
    Creates jobs, searches, and analyses tables with appropriate indexes
    per the data-model.md specification.
    
    Args:
        db_path: Path to the SQLite database file
        
    Raises:
        sqlite3.Error: If database creation fails
        OSError: If path is invalid or not writable
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create tables
        cursor.execute(CREATE_JOBS_TABLE)
        cursor.execute(CREATE_SEARCHES_TABLE)
        cursor.execute(CREATE_ANALYSES_TABLE)
        
        # Create indexes
        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)
        
        conn.commit()
    finally:
        conn.close()


def _job_to_row(job: Job) -> dict:
    """Convert a Job model to a dictionary for SQL insertion.
    
    Args:
        job: Job model instance
        
    Returns:
        Dictionary with job fields as SQL column values
    """
    return {
        "job_url": job.job_url,
        "site": job.site,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "is_remote": job.is_remote,
        "job_type": job.job_type,
        "description": job.description,
        "min_salary": job.min_salary,
        "max_salary": job.max_salary,
        "salary_currency": job.salary_currency,
        "salary_interval": job.salary_interval,
        "date_posted": job.date_posted.isoformat() if job.date_posted else None,
        "job_level": job.job_level,
        "company_industry": job.company_industry,
        "fit_rating": job.fit_rating,
        "status": job.status,
        "search_id": job.search_id,
        "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None,
        "analyzed_at": job.analyzed_at.isoformat() if job.analyzed_at else None,
    }


def _row_to_job(row: sqlite3.Row) -> Job:
    """Convert a SQL row to a Job model.
    
    Args:
        row: SQLite Row instance
        
    Returns:
        Job model instance
    """
    return Job(
        job_url=row["job_url"],
        site=row["site"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        is_remote=bool(row["is_remote"]) if row["is_remote"] is not None else None,
        job_type=row["job_type"],
        description=row["description"],
        min_salary=row["min_salary"],
        max_salary=row["max_salary"],
        salary_currency=row["salary_currency"],
        salary_interval=row["salary_interval"],
        date_posted=date.fromisoformat(row["date_posted"]) if row["date_posted"] else None,
        job_level=row["job_level"],
        company_industry=row["company_industry"],
        fit_rating=row["fit_rating"],
        status=row["status"],
        search_id=row["search_id"],
        scraped_at=datetime.fromisoformat(row["scraped_at"]) if row["scraped_at"] else None,
        analyzed_at=datetime.fromisoformat(row["analyzed_at"]) if row["analyzed_at"] else None,
    )


def upsert_job(job: Job, db_path: Path) -> int:
    """Insert a new job or update an existing one based on job_url.
    
    Uses INSERT OR REPLACE strategy - if job_url exists, updates the record.
    Returns the database ID of the inserted/updated job.
    
    Args:
        job: Job model instance to upsert
        db_path: Path to the SQLite database
        
    Returns:
        Database ID (primary key) of the inserted/updated job
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if job exists
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job.job_url,))
        existing = cursor.fetchone()
        
        row_data = _job_to_row(job)
        
        if existing:
            # Update existing job
            job_id = existing["id"]
            set_clauses = []
            values = []
            for key, value in row_data.items():
                if key != "job_url":  # Don't update job_url as it's the unique key
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            values.append(job_id)
            
            sql = f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(sql, values)
        else:
            # Insert new job
            columns = list(row_data.keys())
            placeholders = ["?"] * len(columns)
            sql = f"INSERT INTO jobs ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(sql, list(row_data.values()))
            job_id = cursor.lastrowid
        
        conn.commit()
        return job_id
    finally:
        conn.close()


def get_jobs_by_status(status: str, db_path: Path) -> List[Job]:
    """Retrieve all jobs with the specified status.
    
    Args:
        status: Job status to filter by ('new', 'applied', 'declined', 'skip')
        db_path: Path to the SQLite database
        
    Returns:
        List of Job model instances matching the status
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM jobs WHERE status = ?", (status,))
        rows = cursor.fetchall()
        return [_row_to_job(row) for row in rows]
    finally:
        conn.close()


def get_jobs_needing_analysis(limit: int, db_path: Path) -> List[Job]:
    """Retrieve jobs that have not been analyzed yet (fit_rating is NULL).
    
    Args:
        limit: Maximum number of jobs to return
        db_path: Path to the SQLite database
        
    Returns:
        List of Job model instances with no fit_rating
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM jobs WHERE fit_rating IS NULL LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [_row_to_job(row) for row in rows]
    finally:
        conn.close()
