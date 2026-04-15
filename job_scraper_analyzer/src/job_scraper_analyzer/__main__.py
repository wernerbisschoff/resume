"""CLI entry point for job_scraper_analyzer."""

import typer

app = typer.Typer(
    name="job-scraper-analyzer",
    help="Job Scraper Analyzer with AI fit rating",
)


@app.command()
def fetch(
    search_terms_file: str = typer.Option(..., "--search-terms", help="Path to search terms file"),
    location: str = typer.Option("Remote", "--location", help="Job location"),
    is_remote: bool = typer.Option(True, "--remote/--no-remote", help="Remote job filter"),
    hours_old: int = typer.Option(168, "--hours-old", help="Jobs from last N hours"),
) -> None:
    """Fetch jobs from job boards."""
    typer.echo(f"Fetching jobs for: {search_terms_file} in {location}")


@app.command()
def analyze(
    batch_size: int = typer.Option(5, "--batch-size", help="Jobs per analysis batch"),
    cv_path: str = typer.Option("W_Bisschoff_CV.tex", "--cv", help="Path to CV file"),
) -> None:
    """Analyze jobs with AI fit rating."""
    typer.echo(f"Analyzing jobs with batch size: {batch_size}")


@app.command()
def review() -> None:
    """Review and manage job analysis results."""
    typer.echo("Opening interactive review...")


if __name__ == "__main__":
    app()
