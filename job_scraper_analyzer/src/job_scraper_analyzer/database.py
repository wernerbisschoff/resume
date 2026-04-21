"""SQLite database layer with CRUD operations for job scraping and analysis."""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Generator, List, Optional, Tuple

from job_scraper_analyzer.models import Analysis, Job


@contextmanager
def _db_connection(db_path: Path, row_factory: bool = False) -> Generator[Tuple[sqlite3.Connection, sqlite3.Cursor], None, None]:
    """Context manager for database connections with optional row_factory.

    Args:
        db_path: Path to the SQLite database
        row_factory: If True, sets row_factory to sqlite3.Row for column access

    Yields:
        Tuple of (connection, cursor)

    Raises:
        sqlite3.Error: If database connection fails
    """
    conn = sqlite3.connect(db_path)
    if row_factory:
        conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        conn.close()


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
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute(CREATE_JOBS_TABLE)
        cursor.execute(CREATE_SEARCHES_TABLE)
        cursor.execute(CREATE_ANALYSES_TABLE)

        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)

        conn.commit()


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
    with _db_connection(db_path, row_factory=True) as (conn, cursor):
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job.job_url,))
        existing = cursor.fetchone()

        row_data = _job_to_row(job)

        if existing:
            job_id = existing["id"]
            set_clauses = []
            values = []
            for key, value in row_data.items():
                if key != "job_url":
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            values.append(job_id)

            cursor.execute(f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = ?", values)
        else:
            columns = list(row_data.keys())
            placeholders = ["?"] * len(columns)
            cursor.execute(
                f"INSERT INTO jobs ({', '.join(columns)}) VALUES ({', '.join(placeholders)})",
                list(row_data.values())
            )
            job_id = cursor.lastrowid

        conn.commit()
        return job_id


def get_jobs_by_status(status: str, db_path: Path) -> List[Job]:
    """Retrieve all jobs with the specified status.

    Args:
        status: Job status to filter by ('new', 'applied', 'declined', 'skip')
        db_path: Path to the SQLite database

    Returns:
        List of Job model instances matching the status
    """
    with _db_connection(db_path, row_factory=True) as (conn, cursor):
        cursor.execute("SELECT * FROM jobs WHERE status = ?", (status,))
        return [_row_to_job(row) for row in cursor.fetchall()]


def get_jobs_needing_analysis(db_path: Path, limit: Optional[int] = None) -> List[Job]:
    """Retrieve jobs that have not been analyzed yet (fit_rating is NULL).

    Args:
        limit: Maximum number of jobs to return, or None for no limit
        db_path: Path to the SQLite database

    Returns:
        List of Job model instances with no fit_rating
    """
    with _db_connection(db_path, row_factory=True) as (conn, cursor):
        if limit is not None:
            cursor.execute("SELECT * FROM jobs WHERE fit_rating IS NULL LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT * FROM jobs WHERE fit_rating IS NULL")
        return [_row_to_job(row) for row in cursor.fetchall()]


def update_job_status(
    job_url: str,
    status: str,
    db_path: Path,
) -> None:
    """Update a job's status.

    Args:
        job_url: The unique job URL identifying the job
        status: Job status to set ('applied', 'declined', 'new')
        db_path: Path to the SQLite database
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute(
            "UPDATE jobs SET status = ? WHERE job_url = ?",
            (status, job_url),
        )
        conn.commit()


def get_jobs_needing_review(db_path: Path) -> List[Job]:
    """Retrieve 'new' jobs sorted by fit_rating (best first), then by date.

    Jobs with fit_rating are shown first (descending), then jobs without
    fit_rating. This ensures best matches are reviewed first.

    Args:
        db_path: Path to the SQLite database

    Returns:
        List of Job model instances with status 'new', sorted by fit_rating
    """
    with _db_connection(db_path, row_factory=True) as (conn, cursor):
        cursor.execute("""
            SELECT * FROM jobs
            WHERE status = 'new'
            ORDER BY
                CASE WHEN fit_rating IS NULL THEN 1 ELSE 0 END,
                fit_rating DESC,
                scraped_at DESC
        """)
        return [_row_to_job(row) for row in cursor.fetchall()]


def update_job_fit_rating(
    job_url: str,
    fit_rating: int,
    db_path: Path,
    status: str = "new",
) -> None:
    """Update a job's fit_rating and analyzed_at timestamp.

    Args:
        job_url: The unique job URL identifying the job
        fit_rating: The fit rating (1-4) from AI analysis
        db_path: Path to the SQLite database
        status: Job status to set (default 'new')
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute(
            """UPDATE jobs
               SET fit_rating = ?, analyzed_at = CURRENT_TIMESTAMP, status = ?
               WHERE job_url = ?""",
            (fit_rating, status, job_url),
        )
        conn.commit()


def store_analysis(analysis: Analysis, db_path: Path) -> int:
    """Store an analysis result to the analyses table.

    Args:
        analysis: Analysis model instance to store
        db_path: Path to the SQLite database

    Returns:
        Database ID of the inserted analysis
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute(
            """INSERT INTO analyses (job_id, batch_id, fit_rating, justification)
               VALUES (?, ?, ?, ?)""",
            (analysis.job_id, analysis.batch_id, analysis.fit_rating, analysis.justification),
        )
        conn.commit()
        return cursor.lastrowid


def clear_all_jobs(db_path: Path) -> int:
    """Delete all jobs from the database.

    Also clears all analysis records since they reference jobs.

    Args:
        db_path: Path to the SQLite database

    Returns:
        Number of jobs deleted
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute("DELETE FROM analyses")
        cursor.execute("DELETE FROM jobs")
        conn.commit()
        return cursor.rowcount


def reset_jobs_for_analysis(db_path: Path, status: str = "new") -> int:
    """Reset jobs for re-analysis by clearing fit_rating and analyzed_at.

    Args:
        db_path: Path to the SQLite database
        status: Status to set for reset jobs (default 'new')

    Returns:
        Number of jobs reset
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute(
            """UPDATE jobs
               SET fit_rating = NULL, analyzed_at = NULL, status = ?
               WHERE fit_rating IS NOT NULL""",
            (status,),
        )
        conn.commit()
        return cursor.rowcount


def get_job_count(db_path: Path) -> int:
    """Get total count of jobs in the database.

    Args:
        db_path: Path to the SQLite database

    Returns:
        Total number of jobs
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute("SELECT COUNT(*) FROM jobs")
        return cursor.fetchone()[0]


def get_analyzed_count(db_path: Path) -> int:
    """Get count of analyzed jobs (jobs with fit_rating).

    Args:
        db_path: Path to the SQLite database

    Returns:
        Number of analyzed jobs
    """
    with _db_connection(db_path) as (conn, cursor):
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE fit_rating IS NOT NULL")
        return cursor.fetchone()[0]
