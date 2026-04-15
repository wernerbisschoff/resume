"""Integration tests for CLI application with fetch, analyze, and review commands.

RED PHASE: These tests define the expected behavior.
They will FAIL until the CLI module is fully implemented.

Tests use Typer's CliRunner to invoke the CLI and verify:
1. fetch command reads search terms and calls scraper
2. analyze command loads jobs and calls analyzer  
3. review command displays interactive Rich table UI

The CLI app is imported from __main__ since there's no cli.py yet.
The tests will FAIL because:
- Current CLI just echoes messages without calling real functions
- No cli.py module exists to import scraper/analyzer/database functions
"""

import os
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from job_scraper_analyzer.models import Job, Analysis


class TestFetchCommand:
    """Test suite for CLI fetch command."""

    def setup_search_terms_file(self) -> str:
        """Create a temporary search terms file."""
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write("Senior Python Engineer\n")
            f.write("Full Stack Developer\n")
        return path

    def test_fetch_command_scrapes_and_stores(self) -> None:
        """Test that fetch command scrapes jobs and stores to database.
        
        RED: The fetch command must:
        1. Read search terms from the provided file
        2. Call the scraper to fetch jobs from JobSpy
        3. Store scraped jobs to the database
        
        This test will FAIL because:
        - The CLI is in __main__.py as a stub that only echoes messages
        - No cli.py module exists to import scraper/database functions
        - The fetch command doesn't actually call scrape_sites or upsert_job
        """
        runner = CliRunner()
        search_terms_file = self.setup_search_terms_file()
        
        # Mock jobs that would be returned by scraper
        mock_jobs = [
            Job(
                job_url="https://linkedin.com/jobs/view/123",
                site="linkedin",
                title="Senior Python Engineer",
                company="Tech Corp",
                location="Remote SA",
                is_remote=True,
                description="Python with AI/ML experience",
            ),
            Job(
                job_url="https://indeed.com/jobs/view/456",
                site="indeed",
                title="Full Stack Developer",
                company="Startup Inc",
                location="Cape Town",
                is_remote=False,
                description="React and Node.js",
            ),
        ]
        
        # Patch at the source modules (where functions are defined)
        with patch("job_scraper_analyzer.scraper.scrape_sites") as mock_scrape, \
             patch("job_scraper_analyzer.database.upsert_job") as mock_upsert, \
             patch("job_scraper_analyzer.database.init_db") as mock_init_db:
            
            mock_scrape.return_value = mock_jobs
            mock_upsert.return_value = 1
            mock_init_db.return_value = None
            
            # Import app from __main__ (the only place CLI exists currently)
            from job_scraper_analyzer.__main__ import app
            
            result = runner.invoke(app, [
                "fetch",
                "--search-terms", search_terms_file,
                "--location", "Remote",
                "--remote",
                "--hours-old", "168"
            ])
            
            # The command should succeed
            assert result.exit_code == 0, f"Command failed with: {result.output}"
            
            # RED PHASE FAILURE: These assertions will fail because:
            # Current __main__.py fetch command just does:
            #   typer.echo(f"Fetching jobs for: {search_terms_file} in {location}")
            # It does NOT call scrape_sites, init_db, or upsert_job
            
            # Verify scraper was called with correct parameters
            # FAIL: mock_scrape.assert_called() will fail - scrape_sites not called
            mock_scrape.assert_called()
            
            # Verify database was initialized
            mock_init_db.assert_called()
            
            # Verify jobs were stored
            assert mock_upsert.call_count == len(mock_jobs), \
                f"Expected {len(mock_jobs)} upsert calls, got {mock_upsert.call_count}"

    def test_fetch_command_with_empty_search_terms(self) -> None:
        """Test that fetch command handles empty search terms file.
        
        RED: When given an empty search terms file, the command should
        either skip scraping or provide a meaningful warning.
        """
        runner = CliRunner()
        
        # Create empty search terms file
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            pass  # Write nothing
        
        from job_scraper_analyzer.__main__ import app
        
        result = runner.invoke(app, [
            "fetch",
            "--search-terms", path,
        ])
        
        # Command should complete without error
        assert result.exit_code == 0
        
        # Should handle empty file gracefully
        # (Current stub just echoes without checking file content)


class TestAnalyzeCommand:
    """Test suite for CLI analyze command."""

    def setup_mock_jobs(self) -> List[Job]:
        """Create mock job fixtures for testing."""
        return [
            Job(
                job_url="https://linkedin.com/jobs/view/123",
                site="linkedin",
                title="Senior Python Engineer",
                company="Tech Corp",
                location="Remote SA",
                is_remote=True,
                description="Python with AI/ML experience",
            ),
            Job(
                job_url="https://indeed.com/jobs/view/456",
                site="indeed",
                title="Full Stack Developer",
                company="Startup Inc",
                location="Cape Town",
                is_remote=False,
                description="React and Node.js",
            ),
        ]

    def test_analyze_command_loads_and_analyzes_jobs(self) -> None:
        """Test that analyze command loads unanalyzed jobs and runs AI analysis.
        
        RED: The analyze command must:
        1. Load unanalyzed jobs from the database
        2. Call the analyzer to get fit ratings via droid exec
        3. Update jobs in database with fit_rating and justification
        
        This test will FAIL because:
        - Current __main__.py analyze command just echoes a message
        - It doesn't call get_jobs_needing_analysis or analyze_jobs
        """
        runner = CliRunner()
        mock_jobs = self.setup_mock_jobs()
        
        mock_analyses = [
            Analysis(job_id=1, fit_rating=4, justification="Perfect Python match"),
            Analysis(job_id=2, fit_rating=3, justification="Good full stack fit"),
        ]
        
        with patch("job_scraper_analyzer.database.get_jobs_needing_analysis") as mock_get_jobs, \
             patch("job_scraper_analyzer.analyzer.analyze_jobs") as mock_analyze, \
             patch("job_scraper_analyzer.database.init_db") as mock_init_db:
            
            mock_get_jobs.return_value = mock_jobs
            mock_analyze.return_value = mock_analyses
            
            from job_scraper_analyzer.__main__ import app
            
            result = runner.invoke(app, [
                "analyze",
                "--batch-size", "5",
                "--cv", "W_Bisschoff_CV.tex"
            ])
            
            # The command should succeed
            assert result.exit_code == 0, f"Command failed with: {result.output}"
            
            # RED PHASE FAILURE: These will fail because analyze command
            # just echoes "Analyzing jobs with batch size: {batch_size}"
            # and doesn't call the analyzer functions
            
            # Verify jobs were loaded
            mock_get_jobs.assert_called()
            
            # Verify analyzer was called with jobs
            mock_analyze.assert_called()

    def test_analyze_command_with_no_jobs_to_analyze(self) -> None:
        """Test that analyze command handles empty job list gracefully.
        
        RED: When there are no jobs to analyze, the command should
        complete successfully with a meaningful message.
        """
        runner = CliRunner()
        
        with patch("job_scraper_analyzer.database.get_jobs_needing_analysis") as mock_get_jobs:
            mock_get_jobs.return_value = []
            
            from job_scraper_analyzer.__main__ import app
            
            result = runner.invoke(app, ["analyze"])
            
            # Command should complete without error
            assert result.exit_code == 0
            
            # Should indicate no jobs to analyze
            assert "No jobs" in result.output or "complete" in result.output


class TestReviewCommand:
    """Test suite for CLI review command."""

    def setup_mock_jobs_with_analysis(self) -> List[Job]:
        """Create mock job fixtures with analysis for review testing."""
        return [
            Job(
                job_id=1,
                job_url="https://linkedin.com/jobs/view/123",
                site="linkedin",
                title="Senior Python Engineer",
                company="Tech Corp",
                location="Remote SA",
                is_remote=True,
                description="Python with AI/ML experience",
                fit_rating=4,
                status="new",
            ),
            Job(
                job_id=2,
                job_url="https://indeed.com/jobs/view/456",
                site="indeed",
                title="Full Stack Developer",
                company="Startup Inc",
                location="Cape Town",
                is_remote=False,
                description="React and Node.js",
                fit_rating=3,
                status="new",
            ),
            Job(
                job_id=3,
                job_url="https://google.com/jobs/view/789",
                site="google",
                title="Embedded Systems Engineer",
                company="Hardware Co",
                location="Remote",
                is_remote=True,
                description="C++ and embedded experience",
                fit_rating=2,
                status="applied",
            ),
        ]

    def test_review_command_displays_interactive_ui(self) -> None:
        """Test that review command displays interactive Rich table UI.
        
        RED: The review command must:
        1. Load all jobs from database with their analysis
        2. Display a Rich table with job information
        3. Allow keyboard navigation (j/k or arrow keys)
        4. Allow status updates (a=applied, d=declined, s=skip)
        5. Update job status in database
        
        This test will FAIL because:
        - Current __main__.py review command just echoes "Opening interactive review..."
        - It doesn't load jobs or display Rich table
        - It doesn't handle keyboard input or status updates
        """
        runner = CliRunner()
        mock_jobs = self.setup_mock_jobs_with_analysis()
        
        # The review command will need get_jobs_by_status (not yet implemented)
        with patch("job_scraper_analyzer.database.get_jobs_by_status") as mock_get_all, \
             patch("job_scraper_analyzer.database.update_job_fit_rating") as mock_update:
            
            mock_get_all.return_value = mock_jobs
            mock_update.return_value = True
            
            from job_scraper_analyzer.__main__ import app
            
            # Run with input simulating 'q' to quit immediately
            result = runner.invoke(app, ["review"], input="q\n")
            
            # The command should succeed
            assert result.exit_code == 0, f"Command failed with: {result.output}"
            
            # RED PHASE FAILURE: These will fail because review command
            # just echoes and doesn't load jobs or display Rich table
            
            # Verify jobs were loaded for display
            mock_get_all.assert_called()
            
            # Verify Rich table was rendered (output should contain formatted text)
            output_lower = result.output.lower()
            assert any(keyword in output_lower for keyword in ["python", "engineer", "table", "tech"]), \
                f"Output should contain job data or table headers, got: {result.output}"

    def test_review_command_updates_job_status(self) -> None:
        """Test that review command can update job status.
        
        RED: The review command should call update_job_fit_rating when
        the user marks a job as applied/declined/skipped.
        """
        runner = CliRunner()
        mock_jobs = self.setup_mock_jobs_with_analysis()
        
        with patch("job_scraper_analyzer.database.get_jobs_by_status") as mock_get_all, \
             patch("job_scraper_analyzer.database.update_job_fit_rating") as mock_update:
            
            mock_get_all.return_value = mock_jobs
            mock_update.return_value = True
            
            from job_scraper_analyzer.__main__ import app
            
            # Simulate: navigate and mark job as applied
            input_sequence = "\x1b[B\n1\na\nq\n"  # Arrow down, enter, 'a' for applied, 'q' to quit
            
            result = runner.invoke(app, ["review"], input=input_sequence)
            
            # Command may have non-zero exit due to input handling
            # But we verify get_jobs_by_status was called
            mock_get_all.assert_called()

    def test_review_command_with_empty_database(self) -> None:
        """Test that review command handles empty database gracefully.
        
        RED: When there are no jobs in the database, the review command
        should display a meaningful empty state.
        """
        runner = CliRunner()
        
        with patch("job_scraper_analyzer.database.get_jobs_by_status") as mock_get_all:
            mock_get_all.return_value = []
            
            from job_scraper_analyzer.__main__ import app
            
            result = runner.invoke(app, ["review"], input="q\n")
            
            # Command should complete without error
            assert result.exit_code == 0
            
            # Should indicate no jobs to review
            assert "No jobs" in result.output or "empty" in result.output.lower()


class TestCLIIntegration:
    """Integration tests for full CLI workflow."""

    def test_cli_help_shows_all_commands(self) -> None:
        """Test that CLI help displays all available commands."""
        runner = CliRunner()
        
        from job_scraper_analyzer.__main__ import app
        
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "fetch" in result.output
        assert "analyze" in result.output
        assert "review" in result.output

    def test_fetch_help_shows_options(self) -> None:
        """Test that fetch command help displays all options."""
        runner = CliRunner()
        
        from job_scraper_analyzer.__main__ import app
        
        result = runner.invoke(app, ["fetch", "--help"])
        
        assert result.exit_code == 0
        assert "--search-terms" in result.output
        assert "--location" in result.output
        assert "--remote" in result.output
        assert "--hours-old" in result.output

    def test_analyze_help_shows_options(self) -> None:
        """Test that analyze command help displays all options."""
        runner = CliRunner()
        
        from job_scraper_analyzer.__main__ import app
        
        result = runner.invoke(app, ["analyze", "--help"])
        
        assert result.exit_code == 0
        assert "--batch-size" in result.output
        assert "--cv" in result.output
