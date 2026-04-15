"""Pydantic models for Job, Search, and Analysis entities."""

from datetime import date, datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Job(BaseModel):
    """Job posting entity with scraped data and analysis results."""

    job_url: str
    site: Literal["linkedin", "indeed", "google"]
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    job_type: Optional[Literal["fulltime", "parttime", "contract", "internship", "temporary"]] = None
    description: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "USD"
    salary_interval: Optional[str] = None
    date_posted: Optional[date] = None
    job_level: Optional[str] = None
    company_industry: Optional[str] = None
    fit_rating: Optional[Literal[1, 2, 3, 4]] = None
    status: Literal["new", "applied", "declined", "skip"] = "new"
    search_id: Optional[int] = None
    scraped_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, v: str) -> str:
        """Validate URL format for job_url."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("job_url must be a valid HTTP/HTTPS URL")
        return v


class Search(BaseModel):
    """Search parameters for job scraping."""

    search_term: str
    location: Optional[str] = None
    is_remote: bool = False
    hours_old: Optional[int] = None
    job_type: Optional[str] = None
    site_name: str = "linkedin,indeed,google"


class Analysis(BaseModel):
    """AI analysis result for a job posting."""

    job_id: int
    batch_id: Optional[str] = None
    fit_rating: Literal[1, 2, 3, 4]
    justification: str
