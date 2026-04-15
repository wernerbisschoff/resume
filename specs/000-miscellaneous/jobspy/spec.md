# Feature Specification: job-scraper-analyzer

## [PROBLEM_STATEMENT]
Create a Python-based CLI tool to scrape job postings from LinkedIn, Indeed, and Google, analyze their fit against a user's CV using AI, and provide an interactive review interface for managing job applications. The tool must handle filter limitations where sites have mutually exclusive filters (e.g., "Remote" vs "Past 7 days") and batch AI analysis to manage token usage.

## [USER_STORIES]

### [STORY_001]
- **Actor**: Job seeker (Senior Software Engineer, 5+ years, Full-stack/Embedded/AI)
- **Action**: Fetch job postings from multiple sites using search terms from a file
- **Outcome**: Jobs are persisted in a local database with metadata for later review
- **Acceptance_Criteria**: GIVEN a list of search terms WHEN the user runs `fetch` THEN jobs are scraped from Indeed, LinkedIn, and Google and stored in SQLite

### [STORY_002]
- **Actor**: Job seeker
- **Action**: Analyze scraped jobs against their CV for fit rating
- **Outcome**: Each job receives a fit rating ("No fit" to "Perfect fit") and the result is stored
- **Acceptance_Criteria**: GIVEN scraped jobs in the database WHEN the user runs `analyze` THEN jobs are batched (5-10) and analyzed via AI, with ratings stored

### [STORY_003]
- **Actor**: Job seeker
- **Action**: Review jobs interactively and mark status
- **Outcome**: Jobs are marked as "applied", "declined", or "skip" for tracking
- **Acceptance_Criteria**: GIVEN jobs in the database WHEN the user runs `review` THEN an interactive CLI displays jobs and allows status updates

### [STORY_004]
- **Actor**: Job seeker
- **Action**: Search with geolocation filters (Remote SA, Hybrid/Office Cape Town)
- **Outcome**: Jobs are filtered/restricted by location as requested
- **Acceptance_Criteria**: GIVEN search terms WHEN the user specifies Remote SA or Hybrid/Office Cape Town THEN results respect these geographic constraints

## [SUCCESS_METRICS]

- **[METRIC_001]**: Jobs scraped per session — Target: 50+ jobs across all sites
- **[METRIC_002]**: Analysis batch completion rate — Target: 95% of batches complete without error
- **[METRIC_003]**: Review coverage — Target: 100% of scraped jobs reviewed within 2 sessions
- **[METRIC_004]**: Filter intersection accuracy — Target: "Remote" + "Past 7 days" results correctly merged

## [CONSTRAINTS]

- **[CONSTRAINT_001]**: Use `uv` for Python project management
- **[CONSTRAINT_002]**: Use `mise` for environment management
- **[CONSTRAINT_003]**: Use `JobSpy` for scraping (LinkedIn, Indeed, Google)
- **[CONSTRAINT_004]**: Use `droid exec` for AI analysis (non-interactive mode)
- **[CONSTRAINT_005]**: Target Remote South Africa and Hybrid/Office Cape Town locations
- **[CONSTRAINT_006]**: No automatic job application — only status marking
- **[CONSTRAINT_007]**: CLI-only interface (no GUI)

## [RATIONALE]
The user needs a local-first, privacy-preserving tool to manage their job search. By scraping jobs proactively and analyzing fit before applying, they can prioritize high-match opportunities. The intersection strategy addresses real-world filter limitations on job sites. Batching AI analysis keeps token usage manageable while providing actionable fit ratings.

## [ANTI_GOALS]
- No automatic submission of job applications
- No graphical user interface (GUI)
- No cloud hosting or server-side components
- No use of alternative scraping libraries beyond JobSpy
- No use of alternative AI tools beyond `droid exec`

## [CRITICAL_DATA_FLOW]
```
Search Terms File → JobSpy Scraper → SQLite DB → AI Batch Analysis (droid exec) → Fit Rating → Interactive Review CLI → Status Update
```

## [ATTACHMENTS]
None

---

**STATUS**: SUCCESS
**FEATURE_SLUG**: 000-miscellaneous
**BRANCH_NAME**: jobspy
**SPEC_PATH**: specs/000-miscellaneous/jobspy/spec.md
**WORKTREE_PATH**: /home/werner-wsl/Development/personal/latex-cv
**ISSUE_NUMBER**: N/A
**NEXT_ACTION**: cd /home/werner-wsl/Development/personal/latex-cv && Run /spec:core:plan
