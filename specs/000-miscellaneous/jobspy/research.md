# Research: job-scraper-analyzer

## [RESEARCH_SUMMARY]

### [TOOLING_ANALYSIS]

| Tool | Version/Status | Integration Point |
|------|----------------|-------------------|
| `uv` | Installed at ~/.local/bin/uv | Python package management |
| `mise` | Installed at ~/.local/bin/mise | Environment/version management |
| `droid` | Installed at ~/.local/bin/droid | AI analysis via `droid exec` |
| `JobSpy` | Submodule at `./JobSpy` | Job scraping library |

### [JOBSPY_CAPABILITIES]

**Core Function**: `scrape_jobs()` returns a Pandas DataFrame with standardized job data.

**Site Support**: linkedin, indeed, zip_recruiter, glassdoor, google, bayt, naukri, bdjobs

**Key Parameters**:
- `site_name`: list of sites to scrape
- `search_term`: job search query
- `location`: geographic location
- `is_remote`: filter for remote jobs
- `hours_old`: filter by posting age
- `job_type`: fulltime, parttime, contract, internship
- `country_indeed`: country code for Indeed

**Filter Limitations (CONFIRMED)**:
- Indeed: `hours_old` OR (`job_type` + `is_remote`) — mutually exclusive
- LinkedIn: `hours_old` OR `easy_apply` — mutually exclusive
- Source: JobSpy model.py and README.md

**Intersection Strategy Required**: For "Remote SA" + "Past 7 days":
1. Run two searches: `is_remote=True` and `hours_old=168`
2. Merge results by job_url deduplication
3. Mark source for each record

### [DROID_EXEC_INTEGRATION]

**Command Structure**: `droid exec --auto <level> "<prompt>"`

**Autonomy Levels**:
- `--auto low`: Low-risk operations
- `--auto medium`: Development operations
- `--auto high`: Production operations

**For AI Analysis**: Use `--auto low` to analyze job fit without interactive overhead.

**Prompt Template Strategy**:
```
Analyze this job posting for fit with the following profile:
[CV Summary]

JOB:
Title: {title}
Company: {company}
Description: {description}

Rate fit as: Perfect | Good | Marginal | No Fit
Justify in 1 sentence.
```

### [CV_CONTEXT_EXTRACTION]

**CV Location**: `W_Bisschoff_CV.tex` with sections in `cv/*.tex`

**Relevant Sections**:
- `cv/summary.tex`: Professional summary
- `cv/skills.tex`: Technical skills (Python, JS, C#, C++, ESP32, AI workflows)
- `cv/experience.tex`: Work history
- `cv/education.tex`: Education

**Strategy**: Parse LaTeX files to extract plain text for AI prompts. Can use simple regex or basic LaTeX parsing.

### [SQLITE_SCHEMA_RATIONALE]

**Jobs Table**: Primary storage for scraped jobs
- Unique constraint on `job_url` to prevent duplicates
- `site` column to track source
- `fit_rating` nullable until analyzed
- `status` for application tracking

**Searches Table**: Track search metadata
- Links to jobs via `search_id`
- Stores search parameters for reproducibility

**Analyses Table**: AI analysis records
- Links job to analysis result
- Batching support via `batch_id`

### [CLI_FRAMEWORK_CHOICE]

**Recommendation**: `typer` over `click`
- Type hints provide automatic CLI help
- Better Pydantic integration for validation
- Rich library complement for UI formatting

### [PROJECT_STRUCTURE]

```
job_scraper_analyzer/
├── pyproject.toml          # uv project config
├── .mise.toml              # mise environment
├── src/
│   └── job_scraper_analyzer/
│       ├── __init__.py
│       ├── cli.py          # typer app with fetch/analyze/review
│       ├── scraper.py      # JobSpy wrapper with intersection logic
│       ├── database.py     # SQLite persistence
│       ├── analyzer.py     # droid exec integration
│       └── models.py       # Pydantic models
├── tests/
│   └── ...
└── quickstart.md
```

### [KEY_RISKS_IDENTIFIED]

1. **Rate Limiting**: LinkedIn is restrictive; JobSpy README confirms ~10 pages before block
2. **LinkedIn Slow Mode**: `linkedin_fetch_description` makes O(n) requests
3. **Filter Conflicts**: Site-specific limitations require intersection strategy
4. **AI Token Usage**: Batching 5-10 keeps prompts manageable

### [CONSTITUTION_STATUS]

- `specs/constitution.md`: **NOT FOUND** — proceeding without constitutional constraints
- No existing project patterns to follow (greenfield)

---

**STATUS**: COMPLETE
**ARTIFACTS**: research.md, data-model.md, plan.md
