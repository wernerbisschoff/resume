"""Tests for opencode AI analyzer for batch job fit rating."""

from datetime import date
from typing import List, Tuple
from unittest.mock import patch, MagicMock

import pytest

from job_scraper_analyzer.models import Job, Analysis


class TestAnalyzeJobs:
    """Test suite for analyze_jobs() batch processing."""

    def setup_test_jobs(self) -> List[Job]:
        """Helper to create test job fixtures."""
        return [
            Job(
                job_url="https://linkedin.com/jobs/view/analyst-1",
                site="linkedin",
                title="Senior Python Engineer",
                company="Tech Corp",
                location="Remote SA",
                is_remote=True,
                description="Looking for Python expert with AI/ML experience",
            ),
            Job(
                job_url="https://linkedin.com/jobs/view/analyst-2",
                site="indeed",
                title="Full Stack Developer",
                company="Startup Inc",
                location="Cape Town",
                is_remote=False,
                description="React and Node.js developer needed",
            ),
            Job(
                job_url="https://linkedin.com/jobs/view/analyst-3",
                site="google",
                title="Embedded Systems Engineer",
                company="Hardware Co",
                location="Remote",
                is_remote=True,
                description="C++ and ESP32 experience required",
            ),
        ]

    def test_analyze_jobs_batch_calls_opencode_run_by_default(self) -> None:
        """Test that analyze_jobs() calls opencode run by default."""
        jobs = self.setup_test_jobs()
        cv_summary = "Senior software engineer with Python, JavaScript, C++ skills"

        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"triage_rating": 3, "justification": "Priority match for Python role"}',
                stderr=""
            )

            from job_scraper_analyzer.analyzer import analyze_jobs

            results = analyze_jobs(jobs, cv_summary, batch_size=2, db_path=None)

            assert mock_run.call_count >= 1

            for call in mock_run.call_args_list:
                args, kwargs = call
                command = args[0] if args else kwargs.get("args", [])
                assert "opencode" in command, "Default backend should be opencode"
                assert "run" in command
                assert "--model" in command

    def test_analyze_jobs_calls_droid_exec_when_backend_is_droid(self) -> None:
        """Test that analyze_jobs() calls droid exec when BACKEND is set to 'droid'."""
        jobs = self.setup_test_jobs()
        cv_summary = "Senior software engineer with Python, JavaScript, C++ skills"

        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"triage_rating": 3, "justification": "Priority match for Python role"}',
                stderr=""
            )

            from job_scraper_analyzer.analyzer import analyze_jobs, BACKEND
            original = BACKEND
            try:
                import job_scraper_analyzer.analyzer as analyzer_mod
                analyzer_mod.BACKEND = "droid"

                results = analyze_jobs(jobs, cv_summary, batch_size=2, db_path=None)

                assert mock_run.call_count >= 1

                for call in mock_run.call_args_list:
                    args, kwargs = call
                    command = args[0] if args else kwargs.get("args", [])
                    assert "droid" in command, "Should call droid exec when BACKEND=droid"
                    assert "exec" in command
            finally:
                analyzer_mod.BACKEND = original

    def test_analyze_jobs_returns_analysis_results(self) -> None:
        """Test that analyze_jobs() returns a list of Analysis objects.
        
        RED: analyze_jobs() must return List[Analysis] with fit_rating and justification.
        """
        jobs = self.setup_test_jobs()
        cv_summary = "Senior software engineer with Python, JavaScript, C++ skills"
        
        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            # Batch mode: single call returns JSON array with all results
            mock_responses = [
                '{"triage_rating": 3, "justification": "Priority match for Python role"}\n{"triage_rating": 2, "justification": "Standard match for full stack"}\n{"triage_rating": 1, "justification": "Backlog fit for embedded"}',
            ]
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=resp, stderr="")
                for resp in mock_responses
            ]
            
            from job_scraper_analyzer.analyzer import analyze_jobs
            
            results = analyze_jobs(jobs, cv_summary, batch_size=5, db_path=None)
            
            assert isinstance(results, list), "analyze_jobs should return a list"
            assert len(results) == 3, "Should return one Analysis per job"
            
            for analysis in results:
                assert isinstance(analysis, Analysis), "Results should be Analysis objects"
                assert analysis.fit_rating in [1, 2, 3, 4], "fit_rating should be 1-4"
                assert analysis.justification, "Each analysis should have a justification"

    def test_analyze_jobs_respects_batch_size(self) -> None:
        """Test that analyze_jobs() processes jobs in batches of the specified size.
        
        RED: Jobs should be grouped into batches of `batch_size`.
        """
        jobs = self.setup_test_jobs()
        cv_summary = "Senior software engineer"
        
        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"fit_rating": 3, "justification": "Good"}',
                stderr=""
            )
            
            from job_scraper_analyzer.analyzer import analyze_jobs
            
            # With 3 jobs and batch_size=2, we expect 2 droid exec calls
            analyze_jobs(jobs, cv_summary, batch_size=2, db_path=None)
            
            # If batching works, we should have 2 calls (first batch of 2, second batch of 1)
            assert mock_run.call_count == 2, "Should make 2 calls for batch_size=2 with 3 jobs"

    def test_analyze_jobs_stores_results_to_database(self) -> None:
        """Test that analyze_jobs() stores results to database when db_path provided.
        
        RED: When db_path is provided, analyze_jobs() should update job fit_ratings in DB.
        """
        import tempfile
        from pathlib import Path
        
        jobs = self.setup_test_jobs()
        cv_summary = "Senior software engineer"
        
        # Create temp database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db = Path(f.name)
        
        try:
            # Initialize database with jobs
            from job_scraper_analyzer.database import init_db, upsert_job
            init_db(temp_db)
            for job in jobs:
                upsert_job(job, temp_db)
            
            with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
                # Batch mode: single call returns JSON array with all results
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout='{"triage_rating": 3, "justification": "Priority match"}\n{"triage_rating": 2, "justification": "Standard match"}\n{"triage_rating": 1, "justification": "Backlog fit"}',
                    stderr=""
                )
                
                from job_scraper_analyzer.analyzer import analyze_jobs
                from job_scraper_analyzer.database import get_jobs_by_status
                
                # Analyze jobs and store to DB
                analyze_jobs(jobs, cv_summary, batch_size=5, db_path=temp_db)
                
                # Verify jobs now have fit_rating in database
                analyzed_jobs = get_jobs_by_status("new", temp_db)
                
                # All analyzed jobs should now have fit_rating set
                for job in analyzed_jobs:
                    assert job.fit_rating is not None, f"Job {job.job_url} should have fit_rating after analysis"
        finally:
            if temp_db.exists():
                temp_db.unlink()


class TestBuildAnalysisPrompt:
    """Test suite for _build_analysis_prompt() helper."""

    def test_build_analysis_prompt_includes_cv_summary(self) -> None:
        """Test that the prompt includes the CV summary.
        
        RED: _build_analysis_prompt() should include cv_summary in the prompt.
        """
        job = Job(
            job_url="https://linkedin.com/jobs/view/test",
            site="linkedin",
            title="Python Engineer",
            company="Tech Corp",
            description="Looking for Python developer",
        )
        cv_summary = "Experienced Python developer with AI/ML skills"
        
        from job_scraper_analyzer.analyzer import _build_analysis_prompt
        
        prompt = _build_analysis_prompt(job, cv_summary)
        
        assert cv_summary in prompt, "Prompt should include the CV summary"
        assert "Python Engineer" in prompt, "Prompt should include job title"
        assert "Tech Corp" in prompt, "Prompt should include company name"
        assert "Looking for Python developer" in prompt, "Prompt should include job description"

    def test_build_analysis_prompt_requests_fit_rating(self) -> None:
        """Test that the prompt asks for a fit rating.
        
        RED: Prompt should ask for fit rating with options: Perfect, Good, Marginal, No Fit.
        """
        job = Job(
            job_url="https://linkedin.com/jobs/view/test",
            site="linkedin",
            title="Engineer",
            company="Co",
            description="Job desc",
        )
        
        from job_scraper_analyzer.analyzer import _build_analysis_prompt
        
        prompt = _build_analysis_prompt(job, "CV summary")
        
        assert "triage" in prompt.lower(), "Prompt should mention triage rating"
        # The rating options should be present
        assert any(opt in prompt for opt in ["EXCLUDE", "BACKLOG", "STANDARD", "PRIORITY", "0", "1", "2", "3"]), \
            "Prompt should include triage rating options"


class TestParseOpencodeResponse:
    """Test suite for _parse_opencode_response() parsing logic."""

    def test_parse_fit_rating_from_response_json(self) -> None:
        """Test parsing JSON response from opencode run."""
        response = '{"triage_rating": 3, "justification": "Priority match for skills"}'

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        fit_rating, justification = _parse_opencode_response(response)

        assert isinstance(fit_rating, int), "triage_rating should be an integer"
        assert fit_rating in [0, 1, 2, 3], "triage_rating should be between 0 and 3"
        assert justification == "Priority match for skills", "justification should be extracted"

    def test_parse_fit_rating_good(self) -> None:
        """Test parsing a STANDARD triage rating response."""
        response = '{"triage_rating": 2, "justification": "Standard match for the role"}'

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        fit_rating, justification = _parse_opencode_response(response)

        assert fit_rating == 2, "triage_rating 2 corresponds to STANDARD"
        assert "Standard match" in justification

    def test_parse_fit_rating_marginal(self) -> None:
        """Test parsing a BACKLOG triage rating response."""
        response = '{"triage_rating": 1, "justification": "Backlog - partial overlap with skills"}'

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        fit_rating, justification = _parse_opencode_response(response)

        assert fit_rating == 1, "triage_rating 1 corresponds to BACKLOG"
        assert "partial overlap" in justification

    def test_parse_fit_rating_no_fit(self) -> None:
        """Test parsing an EXCLUDE triage rating response."""
        response = '{"triage_rating": 0, "justification": "Exclude - significant mismatch"}'

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        fit_rating, justification = _parse_opencode_response(response)

        assert fit_rating == 0, "triage_rating 0 corresponds to EXCLUDE"
        assert "mismatch" in justification.lower()

    def test_parse_opencode_response_handles_text_ratings(self) -> None:
        """Test parsing responses where triage_rating is specified as text."""
        response = '{"triage_rating": "PRIORITY", "justification": "Ideal match"}'

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        fit_rating, justification = _parse_opencode_response(response)

        assert fit_rating == 3, "Text 'PRIORITY' should map to triage_rating 3"
        assert "Ideal match" in justification


class TestAnalyzerEdgeCases:
    """Test suite for edge case handling in analyzer."""

    def test_analyze_jobs_handles_empty_job_list(self) -> None:
        """Test that analyze_jobs() handles empty job list gracefully.
        
        RED: Empty job list should return empty list, not raise an error.
        """
        from job_scraper_analyzer.analyzer import analyze_jobs
        
        results = analyze_jobs([], "CV summary", batch_size=5, db_path=None)
        
        assert results == [], "Empty job list should return empty results"

    def test_parse_opencode_response_handles_malformed_json(self) -> None:
        """Test that _parse_opencode_response() handles malformed JSON gracefully."""
        malformed_response = "This is not valid JSON"

        from job_scraper_analyzer.analyzer import _parse_opencode_response

        with pytest.raises((ValueError, KeyError)):
            _parse_opencode_response(malformed_response)

    def test_analyze_jobs_handles_backend_not_installed(self) -> None:
        """Test handling when the configured backend command is not found."""
        jobs = [
            Job(
                job_url="https://linkedin.com/jobs/view/error",
                site="linkedin",
                title="Engineer",
                company="Co",
                description="Job",
            )
        ]

        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("opencode: command not found")

            from job_scraper_analyzer.analyzer import analyze_jobs

            with pytest.raises(RuntimeError) as exc_info:
                analyze_jobs(jobs, "CV", batch_size=5, db_path=None)

            assert "not installed" in str(exc_info.value).lower()

    def test_analyze_jobs_handles_rate_limiting(self) -> None:
        """Test that analyze_jobs() handles rate limiting from AI service."""
        jobs = [
            Job(
                job_url="https://linkedin.com/jobs/view/ratelimit",
                site="linkedin",
                title="Engineer",
                company="Co",
                description="Job",
            )
        ]
        
        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            # First call fails with rate limit, second succeeds
            mock_run.side_effect = [
                MagicMock(returncode=429, stdout="", stderr="Rate limited"),
                MagicMock(
                    returncode=0,
                    stdout='{"triage_rating": 2, "justification": "Standard"}',
                    stderr=""
                ),
            ]
            
            from job_scraper_analyzer.analyzer import analyze_jobs
            
            # Should either succeed after retry or raise rate limit error
            try:
                results = analyze_jobs(jobs, "CV", batch_size=5, db_path=None, max_retries=1)
                # If it succeeds, rate limiting was handled
                assert len(results) == 1
            except RuntimeError as e:
                # If it raises error, it should be about rate limiting
                assert "rate" in str(e).lower() or "429" in str(e)

    def test_analyze_jobs_includes_batch_id_for_tracking(self) -> None:
        """Test that analysis results include batch_id for audit tracking.
        
        RED: Each Analysis should have a batch_id for tracking which batch it came from.
        """
        jobs = [
            Job(
                job_url="https://linkedin.com/jobs/view/batch",
                site="linkedin",
                title="Engineer",
                company="Co",
                description="Job",
            )
        ]
        
        with patch("job_scraper_analyzer.analyzer.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"triage_rating": 3, "justification": "Priority"}',
                stderr=""
            )
            
            from job_scraper_analyzer.analyzer import analyze_jobs
            
            results = analyze_jobs(jobs, "CV", batch_size=5, db_path=None)
            
            assert len(results) == 1
            assert results[0].batch_id is not None, "Analysis should have batch_id for tracking"
