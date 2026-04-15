# Data Model: job-scraper-analyzer

## [DATABASE_SCHEMA]

**Database**: SQLite at `{WORKTREE}/job_scraper_analyzer/jobs.db`

### [TABLE_JOBS]

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_url TEXT UNIQUE NOT NULL,
    site TEXT NOT NULL,                  -- 'linkedin', 'indeed', 'google'
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    is_remote BOOLEAN,
    job_type TEXT,                       -- 'fulltime', 'parttime', 'contract', 'internship'
    description TEXT,
    min_salary REAL,
    max_salary REAL,
    salary_currency TEXT DEFAULT 'USD',
    salary_interval TEXT,                -- 'yearly', 'hourly', etc.
    date_posted DATE,
    job_level TEXT,                      -- 'Senior', 'Mid', 'Entry', etc.
    company_industry TEXT,
    fit_rating INTEGER,                  -- 1=No Fit, 2=Marginal, 3=Good, 4=Perfect (NULL until analyzed)
    status TEXT DEFAULT 'new',           -- 'new', 'applied', 'declined', 'skip'
    search_id INTEGER,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES searches(id)
);
```

**Indexes**:
```sql
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_site ON jobs(site);
CREATE INDEX idx_jobs_fit_rating ON jobs(fit_rating);
CREATE UNIQUE INDEX idx_jobs_url ON jobs(job_url);
```

### [TABLE_SEARCHES]

```sql
CREATE TABLE searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_term TEXT NOT NULL,
    location TEXT,
    is_remote BOOLEAN,
    hours_old INTEGER,
    job_type TEXT,
    site_name TEXT,                      -- Comma-separated list: 'linkedin,indeed,google'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### [TABLE_ANALYSES]

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    batch_id TEXT,
    fit_rating INTEGER,
    justification TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

## [ENTITY_RELATIONSHIPS]

```
searches (1) ──────< (N) jobs
                          │
                          │ (1) ──────< (N) analyses
                          │
                          └── job_id references jobs.id
```

## [ENUM_VALUES]

### [FIT_RATING]
| Value | Label | Description |
|-------|-------|-------------|
| 1 | No Fit | Significant mismatch |
| 2 | Marginal | Partial overlap |
| 3 | Good | Strong match |
| 4 | Perfect | Ideal fit |

### [JOB_STATUS]
| Value | Label | Description |
|-------|-------|-------------|
| new | New | Not yet reviewed |
| applied | Applied | User has applied |
| declined | Declined | User declined |
| skip | Skip | User skipped |

### [SITE_NAME]
- `linkedin`
- `indeed`
- `google`

### [JOB_TYPE]
- `fulltime`
- `parttime`
- `contract`
- `internship`
- `temporary`

## [PYDANTIC_MODELS]

```python
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Job(BaseModel):
    job_url: str
    site: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "USD"
    salary_interval: Optional[str] = None
    date_posted: Optional[date] = None
    job_level: Optional[str] = None
    company_industry: Optional[str] = None
    fit_rating: Optional[int] = None
    status: str = "new"
    search_id: Optional[int] = None
    scraped_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

class Search(BaseModel):
    search_term: str
    location: Optional[str] = None
    is_remote: Optional[bool] = False
    hours_old: Optional[int] = None
    job_type: Optional[str] = None
    site_name: str = "linkedin,indeed,google"

class Analysis(BaseModel):
    job_id: int
    batch_id: Optional[str] = None
    fit_rating: int
    justification: str
```

## [DATA_FLOW]

1. **Ingest**: User provides search terms file
2. **Scrape**: JobSpy returns DataFrame → convert to `Job` models
3. **Persist**: Jobs inserted to SQLite (upsert on `job_url`)
4. **Analyze**: Batch of 5-10 jobs → `droid exec` → parse rating → store in `analyses`
5. **Review**: Query jobs by status → display interactive CLI → update status

---

**STATUS**: COMPLETE
**SCHEMA_VERSION**: 1.0
**NEXT**: Create plan.md with implementation phases
