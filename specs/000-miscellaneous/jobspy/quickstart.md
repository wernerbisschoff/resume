# Quickstart: job-scraper-analyzer

## [PREREQUISITES]

- Python 3.10+
- `uv` installed
- `mise` installed
- `droid` installed
- Git configured

## [SETUP]

```bash
# Clone the repository
git clone git@github.com:wbisschoff13/Latex-CV.git
cd Latex-CV

# Navigate to the tool directory
cd job_scraper_analyzer

# Install dependencies via mise
mise install

# Verify installation
uv run python --version
```

## [USAGE]

### [FETCH_JOBS]

```bash
# Create a search terms file
echo "senior software engineer" > search_terms.txt
echo "full stack developer" >> search_terms.txt

# Fetch jobs with intersection strategy
uv run job-scraper-analyzer fetch \
  --terms search_terms.txt \
  --location "Cape Town, South Africa" \
  --remote \
  --sites linkedin,indeed,google
```

### [ANALYZE_JOBS]

```bash
# Analyze unrated jobs in batches
uv run job-scraper-analyzer analyze \
  --batch-size 10 \
  --cv ../W_Bisschoff_CV.tex

# Analyze specific jobs by status
uv run job-scraper-analyzer analyze \
  --status new \
  --batch-size 5
```

### [REVIEW_JOBS]

```bash
# Interactive review session
uv run job-scraper-analyzer review

# Review with filters
uv run job-scraper-analyzer review \
  --status applied \
  --fit-rating 4
```

## [COMMANDS]

| Command | Description |
|---------|-------------|
| `fetch` | Scrape jobs from LinkedIn, Indeed, Google |
| `analyze` | Run AI analysis on scraped jobs |
| `review` | Interactive CLI for job status management |
| `list` | List jobs with optional filters |
| `stats` | Show job search statistics |

## [CONFIGURATION]

### [ENVIRONMENT_VARIABLES]

```bash
# Optional: Set a custom database path
export JOB_SCRAPER_DB=/path/to/jobs.db

# Optional: Set search terms file (default: search_terms.txt)
export JOB_SCRAPER_TERMS=/path/to/terms.txt
```

### [SEARCH_TERMS_FILE]

One search term per line:

```
senior software engineer
full stack developer
embedded systems engineer
python developer
ai machine learning
```

## [TROUBLESHOOTING]

### [LINKEDIN_RATE_LIMIT]

If LinkedIn returns 429 errors:
- Wait 5-10 minutes between scrapes
- Use proxies via `--proxies` flag
- Reduce `results-wanted` count

### [DROID_EXEC_SLOW]

If AI analysis is slow:
- Reduce batch size (default: 10)
- Use `--auto low` for minimal agent overhead

### [DATABASE_LOCKED]

If database is locked:
- Ensure no other processes are accessing `jobs.db`
- Check file permissions

---

**For detailed documentation, see `specs/000-miscellaneous/jobspy/`**
