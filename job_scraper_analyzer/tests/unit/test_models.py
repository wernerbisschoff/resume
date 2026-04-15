"""Tests for Pydantic models (Job, Search, Analysis).

RED PHASE: These tests define the expected behavior.
They will FAIL until the models are implemented.
"""

from datetime import date, datetime
from typing import Optional

import pytest
from pydantic import ValidationError

# Import from the models module - this will fail until we implement it
from job_scraper_analyzer.models import Job, Search, Analysis


class TestJobModel:
    """Test suite for Job Pydantic model."""

    def test_job_model_validates_required_fields(self) -> None:
        """Test that missing job_url raises ValidationError.
        
        RED: Job model must enforce job_url as required.
        """
        # Missing required job_url field should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Job(
                site="linkedin",
                title="Software Engineer",
                company="Tech Corp",
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 1
        # Check that job_url is in the error fields
        error_fields = [e.get("loc", [])[0] for e in errors]
        assert "job_url" in error_fields

    def test_job_model_default_status_is_new(self) -> None:
        """Test that status defaults to 'new' when not provided.
        
        RED: Job model must default status to 'new'.
        """
        job = Job(
            job_url="https://linkedin.com/jobs/view/123",
            site="linkedin",
            title="Software Engineer",
        )
        
        assert job.status == "new"

    def test_job_model_accepts_valid_job(self) -> None:
        """Test that Job model accepts all valid fields.
        
        RED: Complete Job model must accept all fields per data-model.md.
        """
        job = Job(
            job_url="https://linkedin.com/jobs/view/456",
            site="linkedin",
            title="Senior Software Engineer",
            company="Tech Corp",
            location="Cape Town, South Africa",
            is_remote=True,
            job_type="fulltime",
            description="Job description here",
            min_salary=80000.0,
            max_salary=120000.0,
            salary_currency="USD",
            salary_interval="yearly",
            date_posted=date(2024, 1, 15),
            job_level="Senior",
            company_industry="Technology",
            fit_rating=4,
            status="new",
        )
        
        assert job.job_url == "https://linkedin.com/jobs/view/456"
        assert job.site == "linkedin"
        assert job.title == "Senior Software Engineer"
        assert job.company == "Tech Corp"
        assert job.location == "Cape Town, South Africa"
        assert job.is_remote is True
        assert job.job_type == "fulltime"
        assert job.description == "Job description here"
        assert job.min_salary == 80000.0
        assert job.max_salary == 120000.0
        assert job.salary_currency == "USD"
        assert job.salary_interval == "yearly"
        assert job.date_posted == date(2024, 1, 15)
        assert job.job_level == "Senior"
        assert job.company_industry == "Technology"
        assert job.fit_rating == 4
        assert job.status == "new"

    def test_job_model_optional_fields_default_to_none(self) -> None:
        """Test that optional fields default to None.
        
        RED: Optional fields must default to None per data-model.md.
        """
        job = Job(
            job_url="https://indeed.com/jobs/view/789",
            site="indeed",
            title="Backend Developer",
        )
        
        assert job.company is None
        assert job.location is None
        assert job.is_remote is None
        assert job.job_type is None
        assert job.description is None
        assert job.min_salary is None
        assert job.max_salary is None
        assert job.salary_interval is None
        assert job.date_posted is None
        assert job.job_level is None
        assert job.company_industry is None
        assert job.fit_rating is None
        assert job.search_id is None
        assert job.scraped_at is None
        assert job.analyzed_at is None

    def test_job_model_salary_currency_defaults_to_usd(self) -> None:
        """Test that salary_currency defaults to 'USD'.
        
        RED: salary_currency must default to 'USD'.
        """
        job = Job(
            job_url="https://google.com/jobs/view/101",
            site="google",
            title="Data Scientist",
        )
        
        assert job.salary_currency == "USD"

    def test_job_model_fit_rating_accepts_integer(self) -> None:
        """Test that fit_rating accepts integer values 1-4.
        
        RED: fit_rating should accept 1 (No Fit) to 4 (Perfect).
        """
        for rating in [1, 2, 3, 4]:
            job = Job(
                job_url=f"https://linkedin.com/jobs/view/{rating}",
                site="linkedin",
                title="Engineer",
                fit_rating=rating,
            )
            assert job.fit_rating == rating

    def test_job_model_status_accepts_valid_statuses(self) -> None:
        """Test that status accepts valid job statuses.
        
        RED: status must accept 'new', 'applied', 'declined', 'skip'.
        """
        valid_statuses = ["new", "applied", "declined", "skip"]
        
        for idx, status in enumerate(valid_statuses):
            job = Job(
                job_url=f"https://linkedin.com/jobs/view/status{idx}",
                site="linkedin",
                title="Engineer",
                status=status,
            )
            assert job.status == status

    def test_job_model_site_accepts_valid_sites(self) -> None:
        """Test that site accepts valid site names.
        
        RED: site must accept 'linkedin', 'indeed', 'google'.
        """
        valid_sites = ["linkedin", "indeed", "google"]
        
        for idx, site in enumerate(valid_sites):
            job = Job(
                job_url=f"https://example.com/jobs/view/{site}{idx}",
                site=site,
                title="Engineer",
            )
            assert job.site == site

    def test_job_model_job_type_accepts_valid_types(self) -> None:
        """Test that job_type accepts valid job types.
        
        RED: job_type must accept 'fulltime', 'parttime', 'contract', 'internship', 'temporary'.
        """
        valid_types = ["fulltime", "parttime", "contract", "internship", "temporary"]
        
        for idx, job_type in enumerate(valid_types):
            job = Job(
                job_url=f"https://linkedin.com/jobs/view/jt{idx}",
                site="linkedin",
                title="Engineer",
                job_type=job_type,
            )
            assert job.job_type == job_type

    def test_job_model_is_remote_boolean(self) -> None:
        """Test that is_remote accepts boolean values.
        
        RED: is_remote must be Optional[bool].
        """
        for is_remote in [True, False, None]:
            job = Job(
                job_url="https://linkedin.com/jobs/view/remote",
                site="linkedin",
                title="Engineer",
                is_remote=is_remote,
            )
            assert job.is_remote is is_remote

    def test_job_model_with_datetime_fields(self) -> None:
        """Test that scraped_at and analyzed_at accept datetime values.
        
        RED: scraped_at and analyzed_at must be Optional[datetime].
        """
        now = datetime(2024, 6, 1, 12, 0, 0)
        job = Job(
            job_url="https://linkedin.com/jobs/view/dt",
            site="linkedin",
            title="Engineer",
            scraped_at=now,
        )
        
        assert job.scraped_at == now
        assert job.analyzed_at is None

    def test_job_model_with_search_id(self) -> None:
        """Test that search_id accepts integer values.
        
        RED: search_id must be Optional[int].
        """
        job = Job(
            job_url="https://linkedin.com/jobs/view/search",
            site="linkedin",
            title="Engineer",
            search_id=42,
        )
        
        assert job.search_id == 42


class TestSearchModel:
    """Test suite for Search Pydantic model."""

    def test_search_model_required_fields(self) -> None:
        """Test that Search model requires search_term.
        
        RED: search_term is required.
        """
        search = Search(search_term="Software Engineer")
        
        assert search.search_term == "Software Engineer"

    def test_search_model_defaults(self) -> None:
        """Test that Search model has correct defaults.
        
        RED: location defaults to None, is_remote defaults to False,
        hours_old defaults to None, job_type defaults to None,
        site_name defaults to 'linkedin,indeed,google'.
        """
        search = Search(search_term="Data Scientist")
        
        assert search.search_term == "Data Scientist"
        assert search.location is None
        assert search.is_remote is False
        assert search.hours_old is None
        assert search.job_type is None
        assert search.site_name == "linkedin,indeed,google"

    def test_search_model_accepts_all_fields(self) -> None:
        """Test that Search model accepts all defined fields.
        
        RED: Complete Search model per data-model.md.
        """
        search = Search(
            search_term="Full Stack Developer",
            location="Cape Town, South Africa",
            is_remote=True,
            hours_old=168,
            job_type="fulltime",
            site_name="linkedin,indeed",
        )
        
        assert search.search_term == "Full Stack Developer"
        assert search.location == "Cape Town, South Africa"
        assert search.is_remote is True
        assert search.hours_old == 168
        assert search.job_type == "fulltime"
        assert search.site_name == "linkedin,indeed"


class TestAnalysisModel:
    """Test suite for Analysis Pydantic model."""

    def test_analysis_model_required_fields(self) -> None:
        """Test that Analysis model requires job_id and fit_rating.
        
        RED: job_id and fit_rating are required.
        """
        analysis = Analysis(
            job_id=1,
            fit_rating=4,
            justification="Perfect match for skills",
        )
        
        assert analysis.job_id == 1
        assert analysis.fit_rating == 4
        assert analysis.justification == "Perfect match for skills"

    def test_analysis_model_defaults(self) -> None:
        """Test that Analysis model has correct defaults.
        
        RED: batch_id defaults to None.
        """
        analysis = Analysis(
            job_id=1,
            fit_rating=3,
            justification="Good match",
        )
        
        assert analysis.job_id == 1
        assert analysis.fit_rating == 3
        assert analysis.justification == "Good match"
        assert analysis.batch_id is None

    def test_analysis_model_fit_rating_range(self) -> None:
        """Test that fit_rating accepts values 1-4.
        
        RED: fit_rating must accept integers 1-4.
        """
        for rating in [1, 2, 3, 4]:
            analysis = Analysis(
                job_id=rating,
                fit_rating=rating,
                justification=f"Rating {rating}",
            )
            assert analysis.fit_rating == rating

    def test_analysis_model_with_batch_id(self) -> None:
        """Test that Analysis model accepts batch_id.
        
        RED: batch_id is Optional[str].
        """
        analysis = Analysis(
            job_id=1,
            fit_rating=4,
            justification="Perfect match",
            batch_id="batch-2024-06-01-001",
        )
        
        assert analysis.batch_id == "batch-2024-06-01-001"
