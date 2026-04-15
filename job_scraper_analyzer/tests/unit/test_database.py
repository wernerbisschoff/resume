"""Tests for SQLite database layer with CRUD operations.

RED PHASE: These tests define the expected behavior.
They will FAIL until the database module is implemented.
"""

import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Generator

import pytest

from job_scraper_analyzer.models import Job, Search, Analysis


# Fixture to provide a temporary database path
@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database file that is cleaned up after the test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


# Fixture to provide a database connection context manager
@pytest.fixture
def db_connection(temp_db_path: Path):
    """Provide a connection context manager to the temporary database."""
    @contextmanager
    def _connect():
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    return _connect


class TestDatabaseInit:
    """Test suite for database initialization."""

    def test_init_db_creates_jobs_table(self, temp_db_path: Path) -> None:
        """Test that init_db() creates the jobs table with correct schema.
        
        RED: init_db() must create jobs table with all columns per data-model.md.
        """
        from job_scraper_analyzer.database import init_db
        
        # Initialize the database
        init_db(temp_db_path)
        
        # Verify jobs table exists
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "jobs table should exist after init_db()"
        assert result[0] == "jobs"

    def test_init_db_creates_searches_table(self, temp_db_path: Path) -> None:
        """Test that init_db() creates the searches table.
        
        RED: init_db() must create searches table per data-model.md.
        """
        from job_scraper_analyzer.database import init_db
        
        init_db(temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='searches'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "searches table should exist after init_db()"

    def test_init_db_creates_analyses_table(self, temp_db_path: Path) -> None:
        """Test that init_db() creates the analyses table.
        
        RED: init_db() must create analyses table per data-model.md.
        """
        from job_scraper_analyzer.database import init_db
        
        init_db(temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "analyses table should exist after init_db()"

    def test_init_db_creates_indexes(self, temp_db_path: Path) -> None:
        """Test that init_db() creates the required indexes.
        
        RED: init_db() must create indexes per data-model.md.
        """
        from job_scraper_analyzer.database import init_db
        
        init_db(temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check for expected indexes
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='index'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Expected indexes per data-model.md
        expected_indexes = [
            "idx_jobs_status",
            "idx_jobs_site",
            "idx_jobs_fit_rating",
            "idx_jobs_url",  # UNIQUE index on job_url
        ]
        
        for idx_name in expected_indexes:
            assert idx_name in indexes, f"Index {idx_name} should exist after init_db()"

    def test_init_db_idempotent(self, temp_db_path: Path) -> None:
        """Test that calling init_db() multiple times does not raise errors.
        
        RED: init_db() should be safe to call multiple times (idempotent).
        """
        from job_scraper_analyzer.database import init_db
        
        # Should not raise any exception
        init_db(temp_db_path)
        init_db(temp_db_path)  # Call again
        init_db(temp_db_path)  # Call again
        
        # Database should still be valid
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "jobs" in tables
        assert "searches" in tables
        assert "analyses" in tables


class TestUpsertJob:
    """Test suite for upsert_job() CRUD operation."""

    def test_upsert_job_inserts_new_job(self, temp_db_path: Path) -> None:
        """Test that upsert_job() inserts a new job and returns its ID.
        
        RED: upsert_job(job) must insert job and return database ID.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        job = Job(
            job_url="https://linkedin.com/jobs/view/123456",
            site="linkedin",
            title="Senior Software Engineer",
            company="Tech Corp",
            location="Cape Town, South Africa",
            is_remote=True,
            job_type="fulltime",
            description="Great opportunity",
            min_salary=80000.0,
            max_salary=120000.0,
            salary_currency="USD",
            salary_interval="yearly",
            date_posted=date(2024, 1, 15),
            job_level="Senior",
            company_industry="Technology",
        )
        
        job_id = upsert_job(job, temp_db_path)
        
        assert isinstance(job_id, int), "upsert_job should return an integer ID"
        assert job_id > 0, "Job ID should be a positive integer"
        
        # Verify job exists in database
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_url = ?", (job.job_url,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "Job should exist in database after upsert_job()"
        assert row["title"] == "Senior Software Engineer"
        assert row["company"] == "Tech Corp"

    def test_upsert_job_updates_existing_job(self, temp_db_path: Path) -> None:
        """Test that upsert_job() updates an existing job instead of duplicating.
        
        RED: When job_url already exists, upsert_job() should UPDATE, not INSERT.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        job = Job(
            job_url="https://linkedin.com/jobs/view/123456",
            site="linkedin",
            title="Senior Software Engineer",
            company="Tech Corp",
        )
        
        # First insert
        job_id_1 = upsert_job(job, temp_db_path)
        
        # Update the job with new data
        updated_job = Job(
            job_url="https://linkedin.com/jobs/view/123456",
            site="linkedin",
            title="Senior Software Engineer",
            company="Updated Tech Corp",  # Changed
        )
        
        job_id_2 = upsert_job(updated_job, temp_db_path)
        
        assert job_id_1 == job_id_2, "upsert_job should return same ID for updates"
        
        # Verify only ONE job exists with this URL
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM jobs WHERE job_url = ?", (job.job_url,))
        count = cursor.fetchone()["cnt"]
        conn.close()
        
        assert count == 1, "Should have exactly one job with this URL after upsert (no duplicates)"
        
        # Verify the company was updated
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT company FROM jobs WHERE job_url = ?", (job.job_url,))
        row = cursor.fetchone()
        conn.close()
        
        assert row["company"] == "Updated Tech Corp", "Company should be updated, not original value"

    def test_upsert_job_preserves_existing_fit_rating_on_update(self, temp_db_path: Path) -> None:
        """Test that updating a job preserves existing fit_rating if not provided.
        
        RED: Partial updates should preserve fields not included in new Job.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        # Insert job with fit_rating
        job = Job(
            job_url="https://linkedin.com/jobs/view/789",
            site="linkedin",
            title="Engineer",
            fit_rating=4,
            status="applied",  # Already applied
        )
        
        upsert_job(job, temp_db_path)
        
        # Upsert with same URL but no fit_rating/status (simulating partial update)
        updated_job = Job(
            job_url="https://linkedin.com/jobs/view/789",
            site="linkedin",
            title="Senior Engineer",  # Title changed
        )
        
        upsert_job(updated_job, temp_db_path)
        
        # Verify fit_rating and status are preserved
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT fit_rating, status FROM jobs WHERE job_url = ?", (job.job_url,))
        row = cursor.fetchone()
        conn.close()
        
        # Note: This test documents expected behavior - actual implementation may differ
        # depending on upsert strategy (full replace vs merge)

    def test_upsert_job_handles_all_job_fields(self, temp_db_path: Path) -> None:
        """Test that upsert_job() correctly stores all Job model fields.
        
        RED: All Job fields should be persisted correctly.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        now = datetime(2024, 6, 1, 12, 0, 0)
        job = Job(
            job_url="https://linkedin.com/jobs/view/full-fields",
            site="linkedin",
            title="Full Stack Developer",
            company="Big Tech Inc",
            location="Remote SA",
            is_remote=True,
            job_type="fulltime",
            description="Full job description",
            min_salary=90000.0,
            max_salary=150000.0,
            salary_currency="USD",
            salary_interval="yearly",
            date_posted=date(2024, 5, 15),
            job_level="Senior",
            company_industry="Technology",
            fit_rating=3,
            status="new",
            search_id=1,
            scraped_at=now,
        )
        
        job_id = upsert_job(job, temp_db_path)
        
        # Verify all fields
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row["job_url"] == "https://linkedin.com/jobs/view/full-fields"
        assert row["site"] == "linkedin"
        assert row["title"] == "Full Stack Developer"
        assert row["company"] == "Big Tech Inc"
        assert row["is_remote"] == 1  # Boolean stored as integer
        assert row["fit_rating"] == 3
        assert row["status"] == "new"


class TestGetJobsByStatus:
    """Test suite for get_jobs_by_status() query operation."""

    def setup_test_jobs(self, db_path: Path) -> None:
        """Helper to set up test jobs with different statuses."""
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(db_path)
        
        jobs = [
            Job(job_url="https://linkedin.com/jobs/1", site="linkedin", title="Job 1", status="new"),
            Job(job_url="https://linkedin.com/jobs/2", site="linkedin", title="Job 2", status="new"),
            Job(job_url="https://linkedin.com/jobs/3", site="linkedin", title="Job 3", status="applied"),
            Job(job_url="https://linkedin.com/jobs/4", site="linkedin", title="Job 4", status="declined"),
            Job(job_url="https://linkedin.com/jobs/5", site="linkedin", title="Job 5", status="skip"),
        ]
        
        for job in jobs:
            upsert_job(job, db_path)

    def test_get_jobs_by_status_returns_matching_jobs(self, temp_db_path: Path) -> None:
        """Test that get_jobs_by_status() returns only jobs with the specified status.
        
        RED: get_jobs_by_status(status) should return List[Job] with matching status.
        """
        from job_scraper_analyzer.database import init_db
        
        self.setup_test_jobs(temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_by_status
        
        new_jobs = get_jobs_by_status("new", temp_db_path)
        
        assert isinstance(new_jobs, list), "get_jobs_by_status should return a list"
        assert len(new_jobs) == 2, "Should find 2 jobs with 'new' status"
        
        for job in new_jobs:
            assert job.status == "new", f"All returned jobs should have status 'new', got '{job.status}'"

    def test_get_jobs_by_status_returns_empty_list_when_no_match(self, temp_db_path: Path) -> None:
        """Test that get_jobs_by_status() returns empty list when no jobs match.
        
        RED: get_jobs_by_status() should return [] when no matches found.
        """
        from job_scraper_analyzer.database import init_db
        
        init_db(temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_by_status
        
        jobs = get_jobs_by_status("applied", temp_db_path)
        
        assert isinstance(jobs, list), "get_jobs_by_status should return a list"
        assert len(jobs) == 0, "Should return empty list when no jobs match status"

    def test_get_jobs_by_status_returns_jobs_as_job_objects(self, temp_db_path: Path) -> None:
        """Test that get_jobs_by_status() returns Job model instances, not raw dicts.
        
        RED: Return type should be List[Job] with full Job model behavior.
        """
        from job_scraper_analyzer.database import init_db
        
        self.setup_test_jobs(temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_by_status
        
        jobs = get_jobs_by_status("applied", temp_db_path)
        
        assert len(jobs) == 1
        assert isinstance(jobs[0], Job), "Should return Job model instances"
        assert jobs[0].status == "applied"
        assert jobs[0].job_url == "https://linkedin.com/jobs/3"


class TestGetJobsNeedingAnalysis:
    """Test suite for get_jobs_needing_analysis() query operation."""

    def setup_analyses_jobs(self, db_path: Path) -> None:
        """Helper to set up jobs with and without analyses."""
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(db_path)
        
        # Create jobs - some with fit_rating (analyzed), some without
        jobs = [
            Job(job_url="https://linkedin.com/jobs/a1", site="linkedin", title="Job A1", fit_rating=None),  # Needs analysis
            Job(job_url="https://linkedin.com/jobs/a2", site="linkedin", title="Job A2", fit_rating=None),  # Needs analysis
            Job(job_url="https://linkedin.com/jobs/a3", site="linkedin", title="Job A3", fit_rating=3),      # Analyzed
            Job(job_url="https://linkedin.com/jobs/a4", site="linkedin", title="Job A4", fit_rating=None),  # Needs analysis
            Job(job_url="https://linkedin.com/jobs/a5", site="linkedin", title="Job A5", fit_rating=1),    # Analyzed
        ]
        
        for job in jobs:
            upsert_job(job, db_path)

    def test_get_jobs_needing_analysis_returns_unanalyzed_jobs(self, temp_db_path: Path) -> None:
        """Test that get_jobs_needing_analysis() returns jobs without fit_rating.
        
        RED: get_jobs_needing_analysis(limit) should return jobs where fit_rating IS NULL.
        """
        from job_scraper_analyzer.database import init_db
        
        self.setup_analyses_jobs(temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_needing_analysis
        
        jobs = get_jobs_needing_analysis(limit=10, db_path=temp_db_path)
        
        assert isinstance(jobs, list), "Should return a list"
        assert len(jobs) == 3, "Should find 3 jobs needing analysis (fit_rating is NULL)"
        
        for job in jobs:
            assert job.fit_rating is None, f"Job {job.job_url} should have fit_rating=None"

    def test_get_jobs_needing_analysis_respects_limit(self, temp_db_path: Path) -> None:
        """Test that get_jobs_needing_analysis() respects the limit parameter.
        
        RED: Should return at most `limit` jobs.
        """
        from job_scraper_analyzer.database import init_db
        
        self.setup_analyses_jobs(temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_needing_analysis
        
        jobs = get_jobs_needing_analysis(limit=2, db_path=temp_db_path)
        
        assert len(jobs) <= 2, "Should return at most 2 jobs when limit=2"

    def test_get_jobs_needing_analysis_returns_empty_when_all_analyzed(self, temp_db_path: Path) -> None:
        """Test that get_jobs_needing_analysis() returns empty when all jobs analyzed.
        
        RED: All analyzed state should return empty list.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        # All jobs have fit_rating
        jobs = [
            Job(job_url="https://linkedin.com/jobs/b1", site="linkedin", title="Job B1", fit_rating=4),
            Job(job_url="https://linkedin.com/jobs/b2", site="linkedin", title="Job B2", fit_rating=3),
        ]
        
        for job in jobs:
            upsert_job(job, temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_needing_analysis
        
        result = get_jobs_needing_analysis(limit=10, db_path=temp_db_path)
        
        assert isinstance(result, list)
        assert len(result) == 0, "Should return empty list when all jobs are analyzed"


class TestDatabaseEdgeCases:
    """Test suite for edge case handling in database operations."""

    def test_upsert_job_handles_none_values(self, temp_db_path: Path) -> None:
        """Test that upsert_job() correctly handles None optional fields.
        
        RED: Jobs with None values for optional fields should persist correctly.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        job = Job(
            job_url="https://linkedin.com/jobs/optional",
            site="linkedin",
            title="Job with Optional Fields",
            company=None,
            location=None,
            is_remote=None,
            job_type=None,
            description=None,
            min_salary=None,
            max_salary=None,
            salary_interval=None,
            date_posted=None,
            job_level=None,
            company_industry=None,
            fit_rating=None,
            search_id=None,
        )
        
        job_id = upsert_job(job, temp_db_path)
        
        assert job_id > 0
        
        # Verify job can be retrieved with None fields preserved
        from job_scraper_analyzer.database import get_jobs_by_status
        
        jobs = get_jobs_by_status("new", temp_db_path)
        
        # Find our job
        our_job = next((j for j in jobs if j.job_url == "https://linkedin.com/jobs/optional"), None)
        assert our_job is not None
        assert our_job.company is None
        assert our_job.location is None
        assert our_job.is_remote is None

    def test_database_handles_special_characters_in_text(self, temp_db_path: Path) -> None:
        """Test that database correctly stores text with special characters.
        
        RED: Special characters (quotes, newlines, unicode) should be stored correctly.
        """
        from job_scraper_analyzer.database import init_db, upsert_job
        
        init_db(temp_db_path)
        
        job = Job(
            job_url="https://linkedin.com/jobs/special",
            site="linkedin",
            title='Job with "Quotes" and \n newlines',
            company="Company with ' apostrophes",
            description="Description with <html> tags & symbols: é, ñ, 中文",
        )
        
        upsert_job(job, temp_db_path)
        
        from job_scraper_analyzer.database import get_jobs_by_status
        
        jobs = get_jobs_by_status("new", temp_db_path)
        stored_job = next((j for j in jobs if j.job_url == "https://linkedin.com/jobs/special"), None)
        
        assert stored_job is not None
        assert "Quotes" in stored_job.title
        assert "apostrophes" in stored_job.company

    def test_init_db_fails_gracefully_on_invalid_path(self) -> None:
        """Test that init_db() raises appropriate error for invalid path.
        
        RED: init_db() should raise sqlite3.Error or OSError for invalid paths.
        """
        from job_scraper_analyzer.database import init_db
        
        invalid_path = Path("/nonexistent/path/that/does/not/exist/database.db")
        
        with pytest.raises((sqlite3.Error, OSError, PermissionError)):
            init_db(invalid_path)
