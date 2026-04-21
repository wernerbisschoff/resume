"""Droid exec AI analyzer for batch job fit rating.

This module handles:
- Batching jobs for AI analysis
- Building prompts for droid exec
- Parsing AI responses for fit ratings
- Storing analysis results to database
"""

import json
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

from job_scraper_analyzer.models import Analysis, Job

# Constants
DROID_TIMEOUT_SECONDS = 120
DROID_NOT_FOUND_CODE = 127
RATE_LIMIT_CODE = 429
MAX_PARALLEL_BATCHES = 5


def analyze_jobs(
    jobs: List[Job],
    cv_summary: str,
    batch_size: int = 5,
    db_path: Optional[Path] = None,
    max_retries: int = 3,
) -> List[Analysis]:
    """Analyze jobs in batches using droid exec for AI analysis.

    Args:
        jobs: List of Job objects to analyze
        cv_summary: CV summary text for context
        batch_size: Number of jobs per batch (default 5)
        db_path: Optional database path for storing results
        max_retries: Maximum retry attempts for failed calls

    Returns:
        List of Analysis objects with fit ratings and justifications
    """
    if not jobs:
        return []

    results: List[Analysis] = []
    batch_id = str(uuid.uuid4())[:8]

    # Process jobs in batches respecting batch_size, with parallel execution
    batches = []
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        batches.append(batch)

    # Process batches in parallel using ThreadPoolExecutor
    total_batches = len(batches)

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_BATCHES) as executor:
        futures = {
            executor.submit(_analyze_batch_combined, batch, cv_summary, batch_id, max_retries, i, total_batches): i
            for i, batch in enumerate(batches)
        }
        # Collect results in order
        batch_results_map = {}
        for future in as_completed(futures):
            batch_idx = futures[future]
            try:
                batch_results_map[batch_idx] = future.result()
            except RuntimeError:
                # Re-raise RuntimeError (e.g., droid not installed) - this is fatal
                raise
            except Exception as e:
                # On failure, return default analysis for all jobs in batch
                batch_results_map[batch_idx] = [
                    Analysis(
                        job_id=0,
                        batch_id=batch_id,
                        fit_rating=2,
                        justification=f"Batch analysis failed: {str(e)[:100]}",
                    )
                    for _ in batches[batch_idx]
                ]

    # Reconstruct results in order
    for batch_idx in sorted(batch_results_map.keys()):
        results.extend(batch_results_map[batch_idx])

    # Store to database if path provided
    if db_path:
        _store_results_to_db(results, db_path, jobs)

    return results


def _call_droid_exec(prompt: str, max_retries: int) -> str:
    """Execute droid exec command and return response.

    Args:
        prompt: Prompt string to send to droid
        max_retries: Maximum retry attempts

    Returns:
        Response text from droid exec

    Raises:
        RuntimeError: If droid exec fails after retries
        FileNotFoundError: If droid command not found
    """
    retries = 0
    while retries <= max_retries:
        try:
            # Write prompt to temp file to avoid argument list limits
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ["droid", "exec", "--auto", "low", "--file", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=DROID_TIMEOUT_SECONDS,
                )
            finally:
                import os
                os.unlink(temp_path)

            if result.returncode == RATE_LIMIT_CODE:
                if retries < max_retries:
                    retries += 1
                    continue
                raise RuntimeError("Rate limited by AI service (429)")

            if result.returncode == DROID_NOT_FOUND_CODE or "not found" in result.stderr.lower():
                raise FileNotFoundError("droid: command not found")

            if result.returncode != 0:
                raise RuntimeError(f"droid exec failed: {result.stderr}")

            return result.stdout.strip()

        except FileNotFoundError as e:
            raise RuntimeError(f"droid not installed: {e}")
        except RuntimeError:
            raise
        except Exception as e:
            if retries < max_retries:
                retries += 1
                continue
            raise RuntimeError(f"droid exec failed after {max_retries} retries: {e}")


def _analyze_batch_combined(
    batch: List[Job],
    cv_summary: str,
    batch_id: str,
    max_retries: int,
    batch_num: int = 0,
    total_batches: int = 0,
) -> List[Analysis]:
    """Analyze a batch of jobs with a combined prompt.

    Args:
        batch: List of jobs in this batch
        cv_summary: CV summary for context
        batch_id: Batch identifier for tracking
        max_retries: Maximum retry attempts
        batch_num: Batch number for logging (0-indexed)
        total_batches: Total number of batches for logging

    Returns:
        List of Analysis objects for this batch
    """
    if total_batches > 1:
        print(f"  Batch {batch_num + 1}/{total_batches}: analyzing {len(batch)} jobs...")

    prompts = [_build_analysis_prompt(job, cv_summary) for job in batch]
    combined_prompt = "\n---\n".join(prompts)

    response_text = _call_droid_exec(combined_prompt, max_retries)
    return _parse_batch_response(response_text, batch, batch_id)


def _analyze_single_job(
    job: Job,
    cv_summary: str,
    batch_id: str,
    max_retries: int,
) -> Analysis:
    """Analyze a single job using droid exec.

    Args:
        job: Job to analyze
        cv_summary: CV summary for context
        batch_id: Batch identifier for tracking
        max_retries: Maximum retry attempts

    Returns:
        Analysis object for the job
    """
    prompt = _build_analysis_prompt(job, cv_summary)

    try:
        response_text = _call_droid_exec(prompt, max_retries)
        fit_rating, justification = _parse_droid_response(response_text)
    except (ValueError, KeyError):
        # Return default analysis if parsing fails
        return Analysis(
            job_id=0,
            batch_id=batch_id,
            fit_rating=2,  # Default to Marginal
            justification="Unable to parse AI response",
        )

    return Analysis(
        job_id=0,  # Job.id not available on Pydantic model
        batch_id=batch_id,
        fit_rating=fit_rating,
        justification=justification,
    )


def _parse_batch_response(
    response: str,
    batch: List[Job],
    batch_id: str,
) -> List[Analysis]:
    """Parse batch response into individual Analysis objects.

    Args:
        response: Raw response from droid exec
        batch: Original batch of jobs
        batch_id: Batch identifier

    Returns:
        List of Analysis objects
    """
    results: List[Analysis] = []

    # Try to extract individual JSON objects from response
    # The response might contain multiple JSON objects or one combined object

    # First, try to find individual fit_rating entries
    lines = response.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to parse as JSON
        try:
            data = json.loads(line)
            if "fit_rating" in data:
                # This is a JSON response for a job
                fit_rating, justification = _parse_droid_response(line)

                # Match to job by position if we have enough results
                if len(results) < len(batch):
                    job = batch[len(results)]
                    results.append(Analysis(
                        job_id=0,  # Job.id not available on Pydantic model
                        batch_id=batch_id,
                        fit_rating=fit_rating,
                        justification=justification,
                    ))
        except json.JSONDecodeError:
            # Look for fit_rating in text format
            if "fit_rating" in line.lower() or any(
                opt in line.lower() for opt in ["perfect", "good", "marginal", "no fit"]
            ):
                try:
                    fit_rating, justification = _parse_droid_response(line)
                    if len(results) < len(batch):
                        job = batch[len(results)]
                        results.append(Analysis(
                            job_id=0,  # Job.id not available on Pydantic model
                            batch_id=batch_id,
                            fit_rating=fit_rating,
                            justification=justification,
                        ))
                except (ValueError, KeyError):
                    pass

    # If no structured results found, try to parse the entire response
    if not results:
        try:
            fit_rating, justification = _parse_droid_response(response)
            for job in batch:
                results.append(Analysis(
                    job_id=0,  # Job.id not available on Pydantic model
                    batch_id=batch_id,
                    fit_rating=fit_rating,
                    justification=justification,
                ))
        except (ValueError, KeyError):
            # Return default analysis if parsing fails
            for job in batch:
                results.append(Analysis(
                    job_id=0,  # Job.id not available on Pydantic model
                    batch_id=batch_id,
                    fit_rating=2,  # Default to Marginal
                    justification="Unable to parse AI response",
                ))

    return results


def _build_analysis_prompt(job: Job, cv_summary: str) -> str:
    """Build analysis prompt for a single job.

    Args:
        job: Job object to analyze
        cv_summary: CV summary text

    Returns:
        Formatted prompt string for droid exec
    """
    prompt = f"""You are evaluating a job posting for fit with a candidate's profile. Provide a thorough, honest assessment.

## CANDIDATE PROFILE

{cv_summary}

## JOB TO ANALYZE

Title: {job.title}
Company: {job.company or 'Not specified'}
Location: {job.location or 'Not specified'}
Remote: {'Yes' if job.is_remote else 'No'}
Description: {job.description or 'No description available'}

---

## EVALUATION CRITERIA

Evaluate the job based on the following dimensions:

### 1. ROLE TYPE FIT (Software Engineering Focus)
- Does this role involve software engineering work (backend, frontend, full-stack, embedded, DevOps, AI/ML, etc.)?
- Is it a clear software engineering position or tangential (e.g., pure IT support, sales engineering without development)?
- Weight heavily toward roles that involve actual software development.

### 2. SENIORITY/EXPERIENCE LEVEL MATCH
Evaluate the experience requirements against the candidate's profile:
- **Duration alignment**: Compare job required duration (e.g., "3+ years") with candidate's actual experience (5+ years total). Is the candidate underqualified (job wants more experience) or overqualified (candidate is a senior who would be bored)?
- **Project complexity match**: Does the job's implied project complexity align with the candidate's demonstrated project depth? For example, embedded real-time systems vs. simple CRUD apps have very different complexity profiles.
- **Leadership/mentorship expectations**: Does the job expect senior-level responsibilities (managing others, architecture decisions) that may or may not align?
- **Not just years, but depth**: 5 years of shallow web dev ≠ 5 years of embedded systems + backend + AI integration. Evaluate the TYPE of experience.

### 3. TECHNICAL STACK OVERLAP
- Map the job's required/implied technologies against the candidate's skills
- Consider not just exact matches but adjacent transferable skills (e.g., Python ↔ Elixir, C++ ↔ embedded Rust, etc.)
- Identify hard gaps (required tech candidate doesn't have) vs. soft gaps (can be learned quickly)

### 4. DOMAIN EXPERTISE
- Does the job's domain (fintech, healthcare, embedded, AI, etc.) align with candidate's experience?
- Are there domain-specific requirements that would be difficult to meet?

### 5. CULTURE & WORK STYLE
- Remote/hybrid preferences match?
- Company size and team structure alignment?
- Engineering culture (startup chaos vs. established processes)?

### 6. CONTRACT TYPE & LOCATION
- Permanent vs. contract alignment with candidate's preferences
- Location constraints (remote preferred, willing to do max 2 days/week on-site in Cape Town)

---

## RESPONSE FORMAT

Rate the fit as one of:
- **Perfect (4)**: Strong alignment on role type, experience level, and technical stack. Candidate would likely be excited and qualified.
- **Good (3)**: Reasonable fit with minor gaps. Candidate could succeed with some ramp-up.
- **Marginal (2)**: Significant gaps in experience level, technical stack, or domain. Would require substantial adaptation.
- **No Fit (1)**: Wrong role type, vastly over/underqualified, or fundamental mismatches.

Respond in JSON format:
{{"fit_rating": <1-4>, "justification": "<2-3 sentence justification explaining your assessment on the key dimensions above>"}}
"""
    return prompt


def _parse_droid_response(response: str) -> Tuple[int, str]:
    """Parse fit rating and justification from droid exec response.

    Args:
        response: Raw response from droid exec

    Returns:
        Tuple of (fit_rating, justification)

    Raises:
        ValueError: If response cannot be parsed
        KeyError: If required fields are missing
    """
    # Try to extract JSON from response
    response = response.strip()

    # Handle text ratings like "Perfect", "Good", etc.
    text_rating_map = {
        "perfect": 4,
        "good": 3,
        "marginal": 2,
        "no fit": 1,
        "no_fit": 1,
    }

    # First try to parse as JSON
    try:
        # Find JSON object in response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            fit_rating = data.get("fit_rating")
            justification = data.get("justification") or ""

            # Handle missing fit_rating
            if fit_rating is None:
                raise ValueError("fit_rating not found in response")

            # Handle text rating in JSON
            if isinstance(fit_rating, str):
                fit_rating_lower = fit_rating.lower().strip()
                if fit_rating_lower in text_rating_map:
                    fit_rating = text_rating_map[fit_rating_lower]
                else:
                    raise ValueError(f"Unknown fit_rating text: {fit_rating}")

            fit_rating = int(fit_rating)

            if fit_rating not in [1, 2, 3, 4]:
                raise ValueError(f"fit_rating must be 1-4, got: {fit_rating}")

            return fit_rating, justification
    except json.JSONDecodeError:
        pass

    # Try to parse text-based response
    response_lower = response.lower()

    # Check for text ratings
    for text, rating in text_rating_map.items():
        if text in response_lower:
            # Extract justification after the rating text
            parts = response.split(str(rating) if isinstance(rating, int) else text, 1)
            if len(parts) > 1:
                justification = parts[1].strip()
                # Clean up common prefixes
                for prefix in [":", "-", ")", ">", "."]:
                    if justification.startswith(prefix):
                        justification = justification[1:].strip()
                return rating, justification[:200]  # Limit length

    # If no recognized format, raise error
    raise ValueError(f"Unable to parse droid response: {response[:100]}")


def _store_results_to_db(
    results: List[Analysis],
    db_path: Path,
    jobs: List[Job],
) -> None:
    """Store analysis results to database.

    Updates both the jobs table (fit_rating) and analyses table.

    Args:
        results: List of Analysis objects
        db_path: Path to SQLite database
        jobs: Original jobs list to map job_url to results
    """
    # Import here to avoid circular dependency
    from job_scraper_analyzer.database import store_analysis, update_job_fit_rating

    # Build a mapping from job_url to analysis result
    job_url_to_analysis = {}
    for i, job in enumerate(jobs):
        if i < len(results):
            job_url_to_analysis[job.job_url] = results[i]

    for job_url, analysis in job_url_to_analysis.items():
        try:
            # Update job's fit_rating in jobs table
            update_job_fit_rating(job_url, analysis.fit_rating, db_path)
            # Store analysis record
            store_analysis(analysis, db_path)
        except Exception:
            # Log but don't fail if storage fails
            pass
