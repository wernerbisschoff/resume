"""CLI entry point for job_scraper_analyzer."""

import os
import sys
import termios
import tty
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from job_scraper_analyzer import analyzer, database, scraper
from job_scraper_analyzer.cv_parser import parse_yaml_resume

# Default database path
DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "job-scraper-analyzer" / "jobs.db"

app = typer.Typer(
    name="job-scraper-analyzer",
    help="Job Scraper Analyzer with AI fit rating",
)
console = Console()

def _get_char() -> str:
    """Get a single character without requiring Enter."""
    try:
        fd = sys.stdin.fileno()
    except OSError:
        return sys.stdin.read(1) if hasattr(sys.stdin, "read") else ""
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def _ensure_db_path(db_path: Optional[Path] = None) -> Path:
    """Ensure database path exists, create parent directories if needed."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


@app.command()
def fetch(
    search_terms_file: str = typer.Option(..., "--search-terms", help="Path to search terms file"),
    location: str = typer.Option("South Africa", "--location", help="Job location"),
    is_remote: bool = typer.Option(True, "--remote/--no-remote", help="Remote job filter"),
    hours_old: int = typer.Option(168, "--hours-old", help="Jobs from last N hours"),
    max_jobs: int = typer.Option(100, "--max-jobs", help="Maximum total jobs to fetch across all sites"),
    linkedin_cookies: Optional[str] = typer.Option(None, "--linkedin-cookies", help="LinkedIn session cookies (li_at) for fetching descriptions"),
    db_path: Optional[Path] = typer.Option(None, "--db", help="Database path"),
    company_denylist: Optional[str] = typer.Option(None, "--denylist", help="Comma-separated list of companies to exclude (or path to .denylist.txt file)"),
) -> None:
    """Fetch jobs from job boards."""
    db_path = _ensure_db_path(db_path)

    # Initialize database
    database.init_db(db_path)

    # Read search terms file
    search_terms_path = Path(search_terms_file)
    if not search_terms_path.exists():
        typer.echo(f"Error: Search terms file not found: {search_terms_file}")
        raise typer.Exit(1)

    search_terms = search_terms_path.read_text().strip().split("\n")
    search_terms = [term.strip() for term in search_terms if term.strip()]

    if not search_terms:
        typer.echo("No search terms found in file.")
        return

    # Use provided cookies or fall back to environment variable
    if linkedin_cookies is None:
        linkedin_cookies = os.environ.get("LINKEDIN_COOKIES")

    # Parse company denylist
    deny_companies: set = set()
    if company_denylist:
        deny_path = Path(company_denylist)
        if deny_path.exists() and deny_path.is_file():
            # Load from file (one company per line)
            deny_companies = {c.strip().lower() for c in deny_path.read_text().split("\n") if c.strip()}
            typer.echo(f"Loaded {len(deny_companies)} companies from denylist file: {deny_path}")
        else:
            # Treat as comma-separated list
            deny_companies = {c.strip().lower() for c in company_denylist.split(",") if c.strip()}
    else:
        # Check for default denylist file in current directory
        default_deny_path = Path("company.denylist.txt")
        if default_deny_path.exists():
            deny_companies = {c.strip().lower() for c in default_deny_path.read_text().split("\n") if c.strip()}
            typer.echo(f"Loaded {len(deny_companies)} companies from default denylist: {default_deny_path}")

    # Scrape jobs with all search terms combined (single scrape call)
    # The scraper will iterate through sites internally
    total_fetched: int = 0
    seen_urls: set = set()  # Deduplicate by job_url
    for term in search_terms:
        typer.echo(f"Fetching jobs for: {term} in {location}...")

        # Use scrape_sites to get LinkedIn and Indeed jobs (50 per site per term)
        # Note: Indeed has mutual exclusion between is_remote and hours_old,
        # so we pass is_remote and filter by date_posted at review stage
        jobs = scraper.scrape_sites(
            search_term=term,
            location=location,
            is_remote=is_remote,
            hours_old=hours_old,
            linkedin_cookies=linkedin_cookies,
            deny_companies=deny_companies,
        )

        # Store jobs incrementally and deduplicate (no max limit)
        new_count = 0
        for job in jobs:
            if job.job_url not in seen_urls:
                database.upsert_job(job, db_path)
                seen_urls.add(job.job_url)
                new_count += 1
                total_fetched += 1

        typer.echo(f"  Found {new_count} new jobs for '{term}' (total: {total_fetched})")

    typer.echo(f"Total: {total_fetched} jobs fetched and stored.")


@app.command()
def analyze(
    batch_size: int = typer.Option(10, "--batch-size", help="Jobs per analysis batch"),
    max_jobs: Optional[int] = typer.Option(None, "--max-jobs", help="Maximum jobs to analyze (default: all unanalyzed)"),
    cv_path: Optional[str] = typer.Option(None, "--cv", help="Path to content/ directory or resume file (default: content/ in repo root)"),
    variant: str = typer.Option("all", "--variant", help="Resume variant: general, systems, infrastructure, or all"),
    db_path: Optional[Path] = typer.Option(None, "--db", help="Database path"),
) -> None:
    """Analyze jobs with AI fit rating."""
    db_path = _ensure_db_path(db_path)

    # Use provided CV path or default to content/ directory
    if cv_path is None:
        content_dir = Path(__file__).parent.parent.parent.parent / "content"
    else:
        content_dir = Path(cv_path)

    # Build CV text from YAML content files (supports variant filtering)
    if content_dir.is_dir() and (content_dir / "config.yaml").exists():
        try:
            cv_text = parse_yaml_resume(content_dir, variant=variant)
            typer.echo(f"Using YAML resume from: {content_dir} (variant: {variant})")
        except Exception as e:
            typer.echo(f"Warning: Could not parse YAML resume: {e}")
            cv_text = "Senior Software Engineer with experience in Python, Full-stack development, and AI/ML."
            typer.echo("Using default summary.")
    elif content_dir.exists() and content_dir.is_file():
        cv_text = content_dir.read_text(encoding="utf-8")
        typer.echo(f"Using CV file: {content_dir}")
    else:
        cv_text = "Senior Software Engineer with experience in Python, Full-stack development, and AI/ML."
        typer.echo(f"CV path not found at {content_dir}, using default summary.")

    # Load jobs needing analysis
    jobs = database.get_jobs_needing_analysis(db_path=db_path) if max_jobs is None else database.get_jobs_needing_analysis(db_path=db_path, limit=max_jobs)

    if not jobs:
        typer.echo("No jobs to analyze.")
        return

    typer.echo(f"Analyzing {len(jobs)} jobs with batch size: {batch_size}")

    # Analyze jobs
    analyses = analyzer.analyze_jobs(jobs, cv_text, batch_size=batch_size, db_path=db_path)

    typer.echo(f"Analysis complete. {len(analyses)} jobs analyzed.")


@app.command()
def review(
    db_path: Optional[Path] = typer.Option(None, "--db", help="Database path"),
    company_denylist: Optional[str] = typer.Option(None, "--denylist", help="Comma-separated list of companies to exclude (or path to .denylist.txt file)"),
) -> None:
    """Review jobs one by one, starting with best matches first."""
    db_path = _ensure_db_path(db_path)

    # Parse company denylist (same logic as fetch)
    deny_companies: set = set()
    if company_denylist:
        deny_path = Path(company_denylist)
        if deny_path.exists() and deny_path.is_file():
            deny_companies = {c.strip().lower() for c in deny_path.read_text().split("\n") if c.strip()}
            typer.echo(f"Loaded {len(deny_companies)} companies from denylist file: {deny_path}")
        else:
            deny_companies = {c.strip().lower() for c in company_denylist.split(",") if c.strip()}
    else:
        # Check for default denylist file in current directory
        default_deny_path = Path("company.denylist.txt")
        if default_deny_path.exists():
            deny_companies = {c.strip().lower() for c in default_deny_path.read_text().split("\n") if c.strip()}
            typer.echo(f"Using {len(deny_companies)} companies from default denylist: {default_deny_path}")

    # Load jobs needing review, sorted by fit_rating (best first)
    jobs = database.get_jobs_needing_review(db_path)

    # Filter out denied companies
    if deny_companies:
        original_count = len(jobs)
        jobs = [j for j in jobs if not (j.company and j.company.lower() in deny_companies)]
        filtered_count = original_count - len(jobs)
        if filtered_count > 0:
            typer.echo(f"Filtered out {filtered_count} jobs from denied companies.")

    if not jobs:
        console.print("[yellow]No jobs to review.[/yellow]")
        return

    console.print(f"\n[cyan]Reviewing {len(jobs)} jobs (best matches first)[/cyan]\n")

    reviewed = 0
    applied = 0
    declined = 0
    skipped = 0

    for i, job in enumerate(jobs, 1):
        # Show job details
        console.print(f"[bold green]--- Job {i}/{len(jobs)} ---[/bold green]")
        console.print(f"[yellow]Title:[/yellow] {job.title or 'N/A'}")
        console.print(f"[yellow]Company:[/yellow] {job.company or 'N/A'}")
        console.print(f"[yellow]Location:[/yellow] {job.location or 'N/A'}")
        console.print(f"[yellow]Fit Rating:[/yellow] {job.fit_rating if job.fit_rating else 'Not analyzed'}")
        console.print(f"[yellow]Site:[/yellow] {job.site or 'N/A'}")
        console.print(f"[yellow]Remote:[/yellow] {'Yes' if job.is_remote else 'No'}")
        console.print(f"[yellow]Link:[/yellow] {job.job_url}")
        console.print()

        # Truncate description for display
        desc = job.description or "No description available."
        if len(desc) > 500:
            desc = desc[:500] + "..."
        console.print(f"[dim]Description:[/dim] {desc}")
        console.print()

        # Prompt for action
        while True:
            console.print("[cyan]Action:[/cyan] \\[a]pplied  \\[d]eclined  \\[s]kip  \\[q]uit: ", end="")
            key = _get_char().lower()

            if key == 'a':
                database.update_job_status(job.job_url, "applied", db_path)
                applied += 1
                reviewed += 1
                console.print("[green]Marked as applied.[/green]")
                break
            elif key == 'd':
                database.update_job_status(job.job_url, "declined", db_path)
                declined += 1
                reviewed += 1
                console.print("[red]Marked as declined.[/red]")
                break
            elif key == 's':
                # Skip - leave status as 'new' so it's picked up next time
                skipped += 1
                console.print("[dim]Skipped.[/dim]")
                break
            elif key == 'q':
                console.print("\n[cyan]Review session ended.[/cyan]")
                console.print(f"Reviewed: {reviewed} | Applied: {applied} | Declined: {declined} | Skipped: {skipped}")
                return
            else:
                console.print("[red]Invalid key. Use a, d, s, or q.[/red]")

        console.print()

    console.print("[bold green]Review complete![/bold green]")
    console.print(f"Reviewed: {reviewed} | Applied: {applied} | Declined: {declined} | Skipped: {skipped}")


@app.command()
def clear(
    mode: str = typer.Argument(..., help="Clear mode: 'jobs' to delete all jobs, 'reset' to reset for re-analysis"),
    db_path: Optional[Path] = typer.Option(None, "--db", help="Database path"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
) -> None:
    """Clear jobs or reset for re-analysis.

    Modes:
        jobs    - Delete all jobs and analyses from database
        reset   - Reset fit ratings to re-analyze all jobs
    """
    db_path = _ensure_db_path(db_path)
    database.init_db(db_path)

    if mode == "jobs":
        job_count = database.get_job_count(db_path)
        if job_count == 0:
            typer.echo("No jobs to clear.")
            return

        if not force:
            confirm = typer.prompt(f"This will delete {job_count} jobs and all analyses. Continue? (y/N)")
            if confirm.lower() != "y":
                typer.echo("Aborted.")
                return

        deleted = database.clear_all_jobs(db_path)
        typer.echo(f"Cleared {deleted} jobs and all analyses.")

    elif mode == "reset":
        analyzed_count = database.get_analyzed_count(db_path)
        if analyzed_count == 0:
            typer.echo("No analyzed jobs to reset.")
            return

        if not force:
            confirm = typer.prompt(f"This will reset {analyzed_count} jobs for re-analysis. Continue? (y/N)")
            if confirm.lower() != "y":
                typer.echo("Aborted.")
                return

        reset = database.reset_jobs_for_analysis(db_path)
        typer.echo(f"Reset {reset} jobs for re-analysis.")

    else:
        typer.echo(f"Unknown mode: {mode}. Use 'jobs' or 'reset'.")
        raise typer.Exit(1)


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\nAborted by user.")
        raise SystemExit(130)
