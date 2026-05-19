"""JobSpy scraper wrapper with intersection strategy for filter limitations."""

import json
import random
import re
import time
import urllib.request
from datetime import date, datetime
from typing import Dict, List, Literal, Optional

from job_scraper_analyzer.models import Job

# Rate limiting delay between queries (seconds)
RATE_LIMIT_DELAY = 2.0

# Max results to fetch per site per search term
MAX_RESULTS_PER_SITE = 50

# Import scrape_jobs at module level - will be mocked in tests
try:
    from jobspy import scrape_jobs
except ImportError:
    scrape_jobs = None


def _extract_rows_from_df(df) -> List[Dict]:
    """Extract row dictionaries from a DataFrame or DataFrame-like mock.

    Handles both real pandas DataFrames and mock objects that emulate
    column-oriented data access.

    Args:
        df: DataFrame or mock object

    Returns:
        List of row dictionaries
    """
    # Handle None
    if df is None:
        return []

    # Check if it's a real pandas DataFrame
    try:
        import pandas as pd
        if isinstance(df, pd.DataFrame):
            if df.empty:
                return []
            return [row.to_dict() for _, row in df.iterrows()]
    except ImportError:
        pass

    # For mock objects or other dict-like structures
    # Mock provides column-oriented access: df["col"] returns list of values
    try:
        # Get column names - try __iter__ first (more reliable for mocks)
        if hasattr(df, '__iter__') and not isinstance(df, type):
            try:
                columns = list(df)
                if columns and not isinstance(columns[0], str):
                    # If columns are not strings, try other methods
                    columns = []
            except (TypeError, ValueError):
                columns = []
        else:
            columns = []

        # If __iter__ didn't work, try keys()
        if not columns and hasattr(df, 'keys'):
            try:
                keys_result = df.keys()
                if hasattr(keys_result, '__iter__') and not isinstance(keys_result, type):
                    columns = list(keys_result)
            except (TypeError, ValueError, AttributeError):
                pass

        if not columns or (len(columns) == 1 and not isinstance(columns[0], str)):
            return []

        # Get number of rows from first column
        first_col = columns[0]
        if not hasattr(df, '__getitem__'):
            return []

        first_values = df[first_col]
        if first_values is None:
            return []
        if not hasattr(first_values, '__len__') or isinstance(first_values, str):
            return []

        num_rows = len(first_values)
        if num_rows == 0:
            return []

        # Build row dicts
        rows = []
        for i in range(num_rows):
            row_dict = {}
            for col in columns:
                col_data = df[col] if hasattr(df, '__getitem__') else None
                if col_data is not None and i < len(col_data):
                    row_dict[col] = col_data[i]
                else:
                    row_dict[col] = None
            rows.append(row_dict)
        return rows

    except (TypeError, KeyError, AttributeError, IndexError):
        return []


def _parse_date_posted(date_value) -> Optional[date]:
    """Parse date_posted from various formats.

    Args:
        date_value: Date as date object, string, or None

    Returns:
        Parsed date or None
    """
    if date_value is None:
        return None
    if isinstance(date_value, date):
        return date_value
    if isinstance(date_value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                pass
    return None


# Countries/regions to consider as South Africa
SOUTH_AFRICA_LOCATIONS = {
    "south africa", "sa", "zuid-afrika",
    "cape town", "johannesburg", "pretoria", "durban", "port elizabeth",
    "bloemfontein", "nairobi", "lagos",  # Include wider Africa tech hubs
    "western cape", "gauteng", "kwazulu-natal",
}

def _is_south_african_job(location: Optional[str]) -> bool:
    """Check if a job location is in South Africa or nearby acceptable region.

    Args:
        location: Job location string from search results

    Returns:
        True if the location is in South Africa or acceptable region
    """
    if not location:
        return False

    loc_lower = location.lower()

    # Check for South Africa explicitly
    # Handle "Remote SA", "Johannesburg, Gauteng, SA", "SA", etc.
    # Must check for word boundary to avoid matching "USA", "Malaysia", etc.
    if "south africa" in loc_lower or loc_lower.strip() == "sa" or loc_lower.endswith(",sa") or loc_lower.endswith(" sa"):
        return True

    # Check for ZA country code (Indeed uses this)
    if ", za" in loc_lower or loc_lower.strip() == "za" or loc_lower.endswith(",za"):
        return True

    # Check for SA provinces
    for region in ["western cape", "gauteng", "kwazulu-natal", "natal",
                   "eastern cape", "limpopo", "mpumalanga", "north west",
                   "free state", "northern cape"]:
        if region in loc_lower:
            return True

    # Check for major SA cities
    for city in ["cape town", "joburg", "sandton", "midrand",
                 "centurion", "east rand", "west rand", "johannesburg",
                 "pretoria", "durban", "port elizabeth", "bloemfontein"]:
        if city in loc_lower:
            return True

    # Check for other acceptable African tech hubs
    for hub in ["nairobi", "lagos", "accra", "cairo"]:
        if hub in loc_lower:
            return True

    # Pure "Remote" without location - allow (flexible for remote-first companies)
    if loc_lower == "remote":
        return True

    return False


def _is_remote_in_location(location: Optional[str]) -> bool:
    """Check if 'remote' is explicitly in the location field (not title/description).

    This is more reliable for LinkedIn jobs where 'Remote' can appear in title
    but the job is actually office-based (e.g., 'GCCA Remote').

    Args:
        location: Job location string

    Returns:
        True if 'remote' is in the location string
    """
    if not location:
        return False
    return "remote" in location.lower()


def _is_remote_acceptable(job_location: Optional[str], job_is_remote: Optional[bool], user_wants_remote: bool) -> bool:
    """Determine if a job's remote status is acceptable based on user preference.

    Args:
        job_location: The job's location string
        job_is_remote: JobSpy's is_remote value for the job
        user_wants_remote: Whether the user requested remote jobs

    Returns:
        True if the job should be accepted based on remote filtering
    """
    if not user_wants_remote:
        # User wants all jobs - accept everything that passed SA filter
        return True

    # User wants remote jobs only
    # Accept if:
    # 1. Location explicitly contains "remote" (e.g., "Remote", "Remote, South Africa")
    # 2. JobSpy says it's remote (is_remote=True) - even with specific SA city location
    if _is_remote_in_location(job_location):
        return True

    if job_is_remote:
        return True

    # Reject jobs with specific SA city locations when they aren't marked as remote
    return False


def _sanitize_value(val, expected_type=None):
    """Sanitize a value from JobSpy DataFrame, handling NaN and None.

    Args:
        val: Raw value from DataFrame
        expected_type: Optional type to coerce the value to

    Returns:
        Sanitized value or None
    """
    import math

    # Handle NaN (float)
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None

    # Handle None
    if val is None:
        return None

    # Handle pandas NA
    try:
        if hasattr(val, '__class__') and 'pandas' in val.__class__.__module__:
            return None
    except Exception:
        pass

    return val


def _convert_jobspy_row(row: Dict) -> Job:
    """Convert a JobSpy DataFrame row dict to a Job model.

    Args:
        row: Dictionary with JobSpy column data

    Returns:
        Job model instance
    """
    return Job(
        job_url=_sanitize_value(row.get("job_url")) or "",
        site=_sanitize_value(row.get("site")) or "linkedin",
        title=_sanitize_value(row.get("title")) or "",
        company=_sanitize_value(row.get("company")),
        location=_sanitize_value(row.get("location")),
        is_remote=_sanitize_value(row.get("is_remote")),
        job_type=_sanitize_value(row.get("job_type")),
        description=_sanitize_value(row.get("description")),
        min_salary=_sanitize_value(row.get("min_salary")),
        max_salary=_sanitize_value(row.get("max_salary")),
        salary_currency=_sanitize_value(row.get("salary_currency")) or "USD",
        salary_interval=_sanitize_value(row.get("salary_interval")),
        date_posted=_parse_date_posted(row.get("date_posted")),
        job_level=_sanitize_value(row.get("job_level")),
        company_industry=_sanitize_value(row.get("company_industry")),
    )


def scrape_sites(
    search_term: str,
    location: str,
    is_remote: bool,
    hours_old: int,
    job_type: Optional[str] = None,
    linkedin_cookies: Optional[str] = None,
    deny_companies: Optional[set] = None,
) -> List[Job]:
    """Scrape job postings from JobSpy-supported sites.

    Args:
        search_term: Job search term
        location: Location to search
        is_remote: Whether to search remote jobs
        hours_old: Filter jobs posted within this many hours
        job_type: Type of job (fulltime, parttime, contract, etc.)
        linkedin_cookies: LinkedIn session cookies for fetching descriptions
        deny_companies: Set of company names to exclude (lowercase)

    Returns:
        List of Job objects
    """
    import sys
    jobs: List[Job] = []
    seen_urls: set = set()
    deny_set = deny_companies or set()

    # Access scrape_jobs through module namespace so tests can patch it
    scraper_module = sys.modules['job_scraper_analyzer.scraper']
    scrape_jobs_func = getattr(scraper_module, 'scrape_jobs', None)
    if scrape_jobs_func is None:
        return []

    try:
        # Search on LinkedIn
        linkedin_df = scrape_jobs_func(
            site_name="linkedin",
            search_term=search_term,
            location=location,
            is_remote=is_remote,
            hours_old=hours_old,
            job_type=job_type,
            results_wanted=MAX_RESULTS_PER_SITE,
            linkedin_fetch_description=True,
            li_at=linkedin_cookies,
            li_oride_dt=True,
        )

        # Convert results to Jobs with deduplication and SA filtering
        # Logic:
        # - When is_remote=True: accept SA jobs that are remote OR any remote job (empty location)
        # - When is_remote=False: accept SA jobs (any type)
        for row_dict in _extract_rows_from_df(linkedin_df):
            try:
                job = _convert_jobspy_row(row_dict)
                is_sa = _is_south_african_job(job.location)
                # Check company denylist
                company_denied = False
                if job.company:
                    company_denied = job.company.lower() in deny_set
                if job.job_url not in seen_urls and not company_denied:
                    if is_sa:
                        if _is_remote_acceptable(job.location, job.is_remote, is_remote):
                            jobs.append(job)
                            seen_urls.add(job.job_url)
                    elif not job.location and job.is_remote:
                        # Empty location but marked as remote - accept when user wants remote
                        if is_remote:
                            jobs.append(job)
                            seen_urls.add(job.job_url)
            except Exception:
                pass

        # Add delay between queries for rate limiting
        time.sleep(RATE_LIMIT_DELAY + random.uniform(0, 1))

        # Search on Indeed
        # Indeed needs country_indeed='south africa' to search SA jobs
        indeed_is_remote = is_remote and location.lower() != "south africa"
        indeed_df = scrape_jobs_func(
            site_name="indeed",
            search_term=search_term,
            location=location,
            country_indeed="south africa",
            is_remote=indeed_is_remote,
            hours_old=None if indeed_is_remote else hours_old,
            job_type=job_type,
            results_wanted=MAX_RESULTS_PER_SITE,
        )

        for row_dict in _extract_rows_from_df(indeed_df):
            try:
                job = _convert_jobspy_row(row_dict)
                is_sa = _is_south_african_job(job.location)
                # Check company denylist
                company_denied = False
                if job.company:
                    company_denied = job.company.lower() in deny_set
                if job.job_url not in seen_urls and not company_denied:
                    if is_sa:
                        if _is_remote_acceptable(job.location, job.is_remote, is_remote):
                            jobs.append(job)
                            seen_urls.add(job.job_url)
                    elif not job.location and job.is_remote:
                        # Empty location but marked as remote - accept when user wants remote
                        if is_remote:
                            jobs.append(job)
                            seen_urls.add(job.job_url)
            except Exception:
                pass

    except Exception:
        # Handle exceptions gracefully - return what we have so far
        pass

    return jobs


def intersection_strategy(
    term: str,
    location: str,
    batch_size: int = 2,
    linkedin_cookies: Optional[str] = None,
    deny_companies: Optional[set] = None,
) -> List[Job]:
    """Execute multiple search variants and merge/deduplicate results.

    This strategy addresses filter limitations where sites have mutually
    exclusive filters (e.g., "Remote" vs "Past 7 days"). It runs multiple
    queries and combines results, removing duplicates by job_url.

    Args:
        term: Search term for jobs
        location: Location to search
        batch_size: Number of search variants to run
        linkedin_cookies: LinkedIn session cookies for fetching descriptions
        deny_companies: Set of company names to exclude (lowercase)

    Returns:
        List of unique Job objects from all searches
    """
    import sys
    all_jobs: List[Job] = []
    seen_urls: set = set()
    deny_set = deny_companies or set()

    # Access scrape_jobs through module namespace so tests can patch it
    scraper_module = sys.modules['job_scraper_analyzer.scraper']
    scrape_jobs_func = getattr(scraper_module, 'scrape_jobs', None)
    if scrape_jobs_func is None:
        return []

    try:
        # Strategy 1: Remote SA with no date filter
        df1 = scrape_jobs_func(
            site_name="linkedin",
            search_term=term,
            location=location,
            is_remote=True,
            hours_old=None,  # No date filter
            results_wanted=MAX_RESULTS_PER_SITE,
            linkedin_fetch_description=True,
            li_at=linkedin_cookies,
            li_oride_dt=True,
        )

        for row_dict in _extract_rows_from_df(df1):
            try:
                job = _convert_jobspy_row(row_dict)
                # Strategy 1: Remote search - use strict remote filtering
                company_denied = job.company and job.company.lower() in deny_set
                if job.job_url not in seen_urls and not company_denied:
                    if _is_south_african_job(job.location):
                        if _is_remote_acceptable(job.location, job.is_remote, user_wants_remote=True):
                            all_jobs.append(job)
                            seen_urls.add(job.job_url)
            except Exception:
                pass

        # Add delay between queries for rate limiting
        time.sleep(RATE_LIMIT_DELAY + random.uniform(0, 1))

        # Strategy 2: Past 7 days (may or may not be remote)
        df2 = scrape_jobs_func(
            site_name="linkedin",
            search_term=term,
            location=location,
            is_remote=False,
            hours_old=168,  # Past 7 days
            results_wanted=MAX_RESULTS_PER_SITE,
            linkedin_fetch_description=True,
            li_at=linkedin_cookies,
            li_oride_dt=True,
        )

        for row_dict in _extract_rows_from_df(df2):
            try:
                job = _convert_jobspy_row(row_dict)
                # Strategy 2: Accept all SA jobs (user wants all jobs)
                company_denied = job.company and job.company.lower() in deny_set
                if job.job_url not in seen_urls and not company_denied:
                    if _is_south_african_job(job.location):
                        if _is_remote_acceptable(job.location, job.is_remote, user_wants_remote=False):
                            all_jobs.append(job)
                            seen_urls.add(job.job_url)
            except Exception:
                pass

    except Exception:
        # Handle exceptions gracefully
        pass

    return all_jobs


def _parse_arc_timestamp(ts: int) -> Optional[date]:
    """Parse Arc postedAt Unix timestamp to date."""
    try:
        return date.fromtimestamp(ts)
    except (ValueError, OSError):
        return None


def _build_arc_url(url_string: str) -> str:
    """Build full Arc job URL from urlString."""
    return f"https://arc.dev/remote-jobs/{url_string}"


def _map_job_type(arc_type: Optional[str]) -> Optional[Literal["fulltime", "parttime", "contract", "internship", "temporary"]]:
    """Map Arc jobType to our job_type enum."""
    mapping = {
        "fulltime": "fulltime",
        "parttime": "parttime",
        "contract": "contract",
        "freelance": "contract",
        "internship": "internship",
        "temporary": "temporary",
    }
    if arc_type:
        return mapping.get(arc_type.lower())
    return None


def scrape_arc(
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    job_type: Optional[str] = None,
    deny_companies: Optional[set] = None,
) -> List[Job]:
    """Scrape jobs from Arc's public remote jobs board.

    Args:
        location: Location filter (e.g. "South Africa", "Worldwide", "Germany")
        experience_level: Experience level filter (e.g. "senior", "mid", "junior", "lead")
        job_type: Job type filter (e.g. "fulltime", "parttime", "contract", "freelance")
        deny_companies: Set of company names to exclude (lowercase)

    Returns:
        List of Job objects from Arc
    """
    jobs: List[Job] = []
    seen_urls: set = set()
    deny_set = deny_companies or set()

    # Build query params
    params = []
    if location:
        params.append(f"location={location.replace(' ', '+')}")
    if experience_level:
        params.append(f"experienceLevel={experience_level}")
    if job_type:
        params.append(f"jobType={job_type}")

    query_string = "&".join(params)
    url = "https://arc.dev/remote-jobs" + ("?" + query_string if query_string else "")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8")

        # Extract __NEXT_DATA__ JSON from the page
        match = re.search(r'__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group(1))
        arc_jobs = data.get("props", {}).get("pageProps", {}).get("arcJobs", [])
        if not arc_jobs:
            return []

        for arc_job in arc_jobs:
            try:
                # Build job URL
                url_string = arc_job.get("urlString", "")
                job_url = _build_arc_url(url_string) if url_string else ""

                # Get company name
                company_data = arc_job.get("company", {})
                company = company_data.get("name") if isinstance(company_data, dict) else None

                # Check denylist
                if company and company.lower() in deny_set:
                    continue

                # Map job type
                mapped_job_type = _map_job_type(arc_job.get("jobType"))

                job = Job(
                    job_url=job_url,
                    site="arc",
                    title=arc_job.get("title", ""),
                    company=company,
                    location=location or "Worldwide",
                    is_remote=True,
                    job_type=mapped_job_type,
                    description=None,  # Arc doesn't expose description in list view
                    min_salary=None,
                    max_salary=None,
                    salary_currency="USD",
                    salary_interval="hourly",
                    date_posted=_parse_arc_timestamp(arc_job.get("postedAt")),
                    job_level=arc_job.get("experienceLevel"),
                    company_industry=None,
                )
                if job_url and job_url not in seen_urls:
                    jobs.append(job)
                    seen_urls.add(job_url)
            except Exception:
                continue

    except Exception:
        pass

    return jobs
