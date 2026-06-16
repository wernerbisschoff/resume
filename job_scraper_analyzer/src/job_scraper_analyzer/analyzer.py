"""AI analyzer for batch job fit rating.

Supports switchable backends:
- opencode (default): uses `opencode run --model minimax/MiniMax-M3`
- droid: uses `droid exec --auto low`

Set the BACKEND constant to switch between them.

This module handles:
- Batching jobs for AI analysis
- Building prompts for the AI backend
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
BACKEND = "opencode"  # Options: "opencode" or "droid"
OPENCODE_MODEL = "minimax/MiniMax-M3"
DROID_TIMEOUT_SECONDS = 300
OPENCODE_TIMEOUT_SECONDS = 300
DROID_NOT_FOUND_CODE = 127
OPENCODE_NOT_FOUND_CODE = 127
RATE_LIMIT_CODE = 429
MAX_PARALLEL_BATCHES = 5
ENGINEERING_TITLE_KEYWORDS = ["engineer", "developer", "programmer"]


def _is_software_engineering_title(title: str) -> bool:
    """Check if job title indicates software engineering or development.

    Deterministic pre-filter to catch clearly non-engineering titles before
    they reach the AI backend. Title must contain at least one keyword from
    ENGINEERING_TITLE_KEYWORDS (case-insensitive).
    """
    if not title:
        return False
    title_lower = title.lower()
    return any(kw in title_lower for kw in ENGINEERING_TITLE_KEYWORDS)


def analyze_jobs(
    jobs: List[Job],
    cv_summary: str,
    batch_size: int = 5,
    db_path: Optional[Path] = None,
    max_retries: int = 3,
) -> List[Analysis]:
    """Analyze jobs in batches using opencode run for AI analysis.

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

    # Pre-filter: auto-exclude clearly non-engineering titles (AI bypass)
    engineering_mask = [_is_software_engineering_title(job.title) for job in jobs]
    engineering_jobs = [job for job, is_eng in zip(jobs, engineering_mask) if is_eng]

    if not engineering_jobs:
        for job in jobs:
            results.append(Analysis(
                job_id=0,
                batch_id=batch_id,
                fit_rating=0,
                justification=f"Non-software title: {job.title}",
            ))
        if db_path:
            _store_results_to_db(results, db_path, jobs)
        return results

    # Process engineering jobs in batches
    batches = []
    for i in range(0, len(engineering_jobs), batch_size):
        batches.append(engineering_jobs[i:i + batch_size])
    total_batches = len(batches)

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_BATCHES) as executor:
        futures = {
            executor.submit(_analyze_batch_combined, batch, cv_summary, batch_id, max_retries, i, total_batches): i
            for i, batch in enumerate(batches)
        }
        batch_results_map = {}
        for future in as_completed(futures):
            batch_idx = futures[future]
            try:
                batch_results_map[batch_idx] = future.result()
            except RuntimeError:
                raise
            except Exception as e:
                batch_results_map[batch_idx] = [
                    Analysis(
                        job_id=0,
                        batch_id=batch_id,
                        fit_rating=1,
                        justification=f"Batch analysis failed: {str(e)[:100]}",
                    )
                    for _ in batches[batch_idx]
                ]

    # Reconstruct engineering results in order
    engineering_results: List[Analysis] = []
    for batch_idx in sorted(batch_results_map.keys()):
        engineering_results.extend(batch_results_map[batch_idx])

    # Merge back into original order, slotting pre-excluded entries
    eng_iter = iter(engineering_results)
    for job, is_eng in zip(jobs, engineering_mask):
        if is_eng:
            result = next(eng_iter, None)
            if result is not None:
                results.append(result)
            else:
                results.append(Analysis(
                    job_id=0,
                    batch_id=batch_id,
                    fit_rating=1,
                    justification="Missing AI result — batch response incomplete",
                ))
        else:
            results.append(Analysis(
                job_id=0,
                batch_id=batch_id,
                fit_rating=0,
                justification=f"Non-software title: {job.title}",
            ))

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


def _call_opencode_run(prompt: str, max_retries: int) -> str:
    """Execute opencode run command and return response.

    Args:
        prompt: Prompt string to send to opencode
        max_retries: Maximum retry attempts

    Returns:
        Response text from opencode

    Raises:
        RuntimeError: If opencode fails after retries
        FileNotFoundError: If opencode command not found
    """
    retries = 0
    while retries <= max_retries:
        try:
            result = subprocess.run(
                ["opencode", "run", "--model", OPENCODE_MODEL, "--dangerously-skip-permissions"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=OPENCODE_TIMEOUT_SECONDS,
            )

            if result.returncode == OPENCODE_NOT_FOUND_CODE or "not found" in result.stderr.lower():
                raise FileNotFoundError("opencode: command not found")

            if result.returncode == RATE_LIMIT_CODE:
                if retries < max_retries:
                    retries += 1
                    continue
                raise RuntimeError("Rate limited by AI service (429)")

            if result.returncode != 0:
                raise RuntimeError(f"opencode run failed: {result.stderr}")

            return result.stdout.strip()

        except FileNotFoundError as e:
            raise RuntimeError(f"opencode not installed: {e}")
        except RuntimeError:
            raise
        except subprocess.TimeoutExpired:
            if retries < max_retries:
                retries += 1
                continue
            raise RuntimeError(f"opencode run timed out after {max_retries} retries")
        except Exception as e:
            if retries < max_retries:
                retries += 1
                continue
            raise RuntimeError(f"opencode run failed after {max_retries} retries: {e}")


def _call_ai_backend(prompt: str, max_retries: int) -> str:
    """Dispatch to the configured AI backend.

    Args:
        prompt: Prompt string to send
        max_retries: Maximum retry attempts

    Returns:
        Response text from the AI backend
    """
    if BACKEND == "droid":
        return _call_droid_exec(prompt, max_retries)
    return _call_opencode_run(prompt, max_retries)


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

    response_text = _call_ai_backend(combined_prompt, max_retries)
    return _parse_batch_response(response_text, batch, batch_id)


def _analyze_single_job(
    job: Job,
    cv_summary: str,
    batch_id: str,
    max_retries: int,
) -> Analysis:
    """Analyze a single job using opencode run.

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
        response_text = _call_ai_backend(prompt, max_retries)
        fit_rating, justification = _parse_opencode_response(response_text)
    except (ValueError, KeyError):
        return Analysis(
            job_id=0,
            batch_id=batch_id,
            fit_rating=1,
            justification="Unable to parse AI response",
        )

    return Analysis(
        job_id=0,
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
        response: Raw response from opencode
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
                fit_rating, justification = _parse_opencode_response(line)

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
                    fit_rating, justification = _parse_opencode_response(line)
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
            fit_rating, justification = _parse_opencode_response(response)
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
                    fit_rating=1,  # Default to BACKLOG on parse failure
                    justification="Unable to parse AI response",
                ))

    return results


def _build_analysis_prompt(job: Job, cv_summary: str) -> str:
    """Build analysis prompt for a single job.

    Args:
        job: Job object to analyze
        cv_summary: CV summary text

    Returns:
        Formatted prompt string for opencode
    """
    prompt = f"""[DOMAIN]: JOB_SCREENING_CLASSIFICATION
[PERSONA]: ELITE_TECHNICAL_RECRUITER — STRICT CLASSIFIER
[OBJECTIVE]: Classify this job posting. Only accept hands-on Software Engineering or Software Development roles.

## [MANDATORY_RULES]
1. STRICT CLASSIFIER ONLY. Do NOT give recommendations, advice, or suggestions. Only output the JSON classification.
2. ONLY Software Engineering and Software Development roles are accepted. IT support, sysadmin, QA (manual), data entry, sales, marketing, admin, recruiting, customer success, finance, design, and technical writing are EXCLUDED.
3. Use the EXACT title and description below. Do NOT infer or hallucinate details. If the title is non-engineering, EXCLUDE immediately regardless of description keywords.
4. If uncertain, EXCLUDE (0). Do NOT default to a middle rating.

## [CV_SUMMARY]
{cv_summary}
[/CV_SUMMARY]

**CRITICAL**: This candidate is a hands-on Software Engineer, NOT a salesperson, NOT an admin, NOT a recruiter. They write code (Python, C/C++, Elixir, TypeScript). If the role does not primarily involve writing/architecting/testing production code, it is NOT a fit.

**NOTE**: The CV_SUMMARY may contain multiple persona variants:
- **general**: Software Engineer (full-stack + embedded + automation)
- **systems**: Hybrid Edge/Systems Engineer (C/C++, FreeRTOS, Elixir/OTP, real-time)
- **infrastructure**: Cloud Infrastructure Engineer / Platform Developer (Python, Docker, AWS, PostgreSQL, Pulumi)

Evaluate the job against ALL variants present and report which variant(s) it matches best.

## [LOCATION_CONSTRAINTS]
- Ideal: Fully remote
- Acceptable: Up to 2 days/week on-site in Cape Town, South Africa
- Desperate Mode: More days in office in Cape Town acceptable if role is otherwise strong

## [JOB_TO_ANALYZE]
Title: {job.title}
Company: {job.company or 'Not specified'}
Location: {job.location or 'Not specified'}
Remote: {'Yes' if job.is_remote else 'No'}
Description: {job.description or 'No description available'}
[/JOB_TO_ANALYZE]

---

## [STEP_1]: HARD EXCLUSION — TITLE CHECK (MANDATORY, BEFORE DESCRIPTION)
**CRITICAL RULE**: Evaluate the TITLE FIRST. The title alone is sufficient to reject. Do NOT let the description override the title — descriptions of non-engineering roles often mention tech keywords (e.g., "SaaS", "Python", "AI", "platform") to attract applicants. Ignore those keywords if the title is non-engineering.

### Exclude (triage_rating = 0) if title contains ANY of:
- **Sales/biz**: sales, sdr, account executive, account manager, business development, growth
- **Admin/office**: executive assistant, personal assistant, admin assistant, office manager, receptionist
- **Customer/account**: customer success, customer support, account support, client success
- **Marketing/recruiting**: marketing, content, social media, seo, recruiter, talent acquisition, hr, people operations
- **Finance/accounting**: accountant, finance, accounting, bookkeeper, auditor, payroll
- **IT support**: IT support, helpdesk, IT technician, desktop support, service desk
- **Management (non-technical)**: project manager, program manager, scrum master, agile coach, product owner
- **Other non-engineering**: technical writer, graphic designer, data entry, business analyst, operations manager, office administrator

### Examples of misleading descriptions to IGNORE:
- "Accountant @ crypto SaaS company" → title is "Accountant", **EXCLUDE**. The "SaaS" and "crypto" in the description do not make this a software role.
- "Customer Success Manager at tech company" → title is "Customer Success Manager", **EXCLUDE**. Relationship management is not software engineering.
- "Growth Marketing Manager (B2B)" → title is "Growth Marketing Manager", **EXCLUDE**. Marketing is not software engineering.

If title triggers → triage_rating = 0, rejection_trigger_if_any = "Non-software title: <title>".

---

## [STEP_2]: DESCRIPTION-BASED NON-SOFTWARE CHECK (only if title passed Step 1)
Primary daily responsibility is NOT writing/architecting/testing code. Examples: sales/SDR/business development, executive/personal assistant, administrative support, office manager, receptionist, customer service/support, marketing, HR/recruiting, finance/accounting, project manager (non-technical), product manager (non-technical), business analyst, data entry, IT support/helpdesk (no coding), manual QA (no coding), sales engineering without dev, technical writing, graphic design, pure IT/hardware. Low-level firmware (C/C++, FreeRTOS) IS software engineering.

If triggered → triage_rating = 0, rejection_trigger_if_any = "<reason>".

---

## [STEP_3]: MULTI-DIMENSIONAL ANALYSIS
If passing Step 1 and Step 2, evaluate:

1. **Seniority & Depth**: Role complexity vs candidate capability (5+ years cross-disciplinary: Embedded C++/FreeRTOS + Full-stack Python/React/Elixir + Cloud infrastructure/AWS + Agentic AI workflows). Not years, depth.
2. **Technical Stack Overlap**:
   - Consider ALL three profiles (general/systems/infrastructure) from CV
   - Core Matches: Python, C/C++, SQL/PostgreSQL, Docker, AWS, Linux, Git, CI/CD
   - Systems Matches: FreeRTOS, ESP32/ESP-IDF, BLE/NimBLE, NFC APDU, UART/SPI/I2C, Elixir/OTP, Cap'n Proto
   - Infrastructure Matches: Docker Compose, Pulumi (IaC), PostgreSQL RLS/Tuning, ERPNext/Frappe, Elixir/Phoenix, Inngest/Oban
   - Strategic Adjacencies: AWS Cert in progress, Phoenix LiveView, Ecto, Pulumi
   - Hard Gaps: Mandatory tech missing with high learning curve
3. **Location & Work Style**: Remote preference weighted highest; 1-2 days hybrid acceptable; more days in Cape Town acceptable only in desperate mode and if role is otherwise strong.

---

## [STEP_4]: OUTPUT FORMULATION
Generate `analytical_scratchpad` BEFORE `triage_rating`. Rating MUST derive from analysis.

```json
{{
  "binary_filters": {{
    "is_software_engineering": true/false,
    "rejection_trigger_if_any": "N/A or <reason>"
  }},
  "analytical_scratchpad": {{
    "seniority_match_critique": "<2-sentence role complexity vs candidate capability>",
    "stack_overlap_critique": "<explicit enumeration: exact matches, soft gaps, hard gaps>",
    "workstyle_critique": "<remote/hybrid/in-office preference alignment>"
  }},
  "scoring_matrix": {{
    "seniority_score": 1-5,
    "stack_score": 1-5,
    "workstyle_score": 1-5
  }},
  "triage_rating": 0-3,
  "actionable_justification": "<2-sentence synthesis including downstream action>"
}}
```

**CRITICAL**: Generate scratchpad fields BEFORE triage_rating. Do NOT reverse order.

---

## [EDGE_CASE_HANDLING]
- CV_SUMMARY empty → use generic senior engineer profile with 5+ years multi-stack experience.
- Job description missing/empty → lean toward evaluation based on title; if title is ambiguous/empty, mark is_software_engineering=false, rejection_trigger_if_any="No job description provided".
- Location field absent → evaluate based on "Remote" flag if present; if both absent, proceed with evaluation without workstyle penalty.
- "Hybrid" keyword without percentage → weight as negative signal for workstyle_score but not exclusion.

---

## [TRIAGE_SCALE]
Apply this strict 3-tier scale:

| Rating | Class | Criteria |
|--------|-------|----------|
| 0 | EXCLUDE | Fails binary filter (non-software) or fundamental tech mismatch. |
| 1 | BACKLOG | Passes binary filter but has significant gaps — hard gaps, low seniority/stack alignment, or workstyle conflicts. |
| 3 | PRIORITY | Strong match — scoring_matrix average ≥ 4, no hard gaps, strong workstyle alignment. |

**CRITICAL**: Rating 2 (STANDARD) is DISABLED. Do NOT use it. If not a clear PRIORITY (3), classify as BACKLOG (1) or EXCLUDE (0).

**Scoring Rules:**
- triage_rating 0 (EXCLUDE): Fails binary filter (is_software_engineering=false) or fundamental tech mismatch.
- triage_rating 1 (BACKLOG): Passes binary filter but scoring_matrix average < 4 OR any hard gaps exist.
- triage_rating 3 (PRIORITY): scoring_matrix average ≥ 4 across all dimensions, no hard gaps, strong stack overlap.

---

## [EXAMPLES]

### Example 1: Backend/Infrastructure match
Input:
```
Title: Senior Platform Engineer
Company: CloudCo
Location: Remote
Description: Build and maintain Kubernetes infrastructure, CI/CD pipelines, and developer tooling. Python and AWS required. PostgreSQL experience a plus.
```

Output:
```json
{{
  "binary_filters": {{
    "is_software_engineering": true,
    "rejection_trigger_if_any": "N/A"
  }},
  "analytical_scratchpad": {{
    "seniority_match_critique": "Role demands platform engineering skills — candidate's infrastructure variant covers Docker, AWS, CI/CD, and Linux systems administration. Seniority aligns well.",
    "stack_overlap_critique": "Core Match: Python, AWS, Docker, CI/CD, PostgreSQL. Variant match: infrastructure profile. Adjacent: Pulumi IaC maps to infrastructure-as-code needs. Hard gaps: Kubernetes not explicitly listed but Docker/container experience transfers.",
    "workstyle_critique": "Fully remote — ideal alignment."
  }},
  "scoring_matrix": {{
    "seniority_score": 4,
    "stack_score": 4,
    "workstyle_score": 5
  }},
  "triage_rating": 3,
  "actionable_justification": "Strong infrastructure profile match with Python, AWS, Docker, and PostgreSQL alignment. Fully remote. Best variant: infrastructure. PRIORITY queue for tailored cover letter."
}}
```

### Example 2: Systems/Embedded match
Input:
```
Title: Embedded Linux Engineer
Company: Hardware Inc
Location: Remote
Description: Develop firmware for IoT devices using C/C++ on ARM Cortex-M. Experience with BLE wireless protocols and real-time constraints.
```

Output:
```json
{{
  "binary_filters": {{
    "is_software_engineering": true,
    "rejection_trigger_if_any": "N/A"
  }},
  "analytical_scratchpad": {{
    "seniority_match_critique": "Role demands embedded C/C++ and real-time firmware experience — candidate's systems variant covers FreeRTOS, ESP32, BLE/NimBLE, and bare-metal runtimes. Strong alignment.",
    "stack_overlap_critique": "Core Match: C/C++, BLE/NimBLE, real-time constraints. Variant match: systems profile. Strategic Adjacency: FreeRTOS and ESP-IDF experience maps to ARM Cortex-M constraints. No hard gaps.",
    "workstyle_critique": "Fully remote — ideal alignment."
  }},
  "scoring_matrix": {{
    "seniority_score": 5,
    "stack_score": 5,
    "workstyle_score": 5
  }},
  "triage_rating": 3,
  "actionable_justification": "Exceptional systems profile match with embedded C++, BLE, and real-time firmware experience. Best variant: systems. PRIORITY queue for tailored cover letter."
}}
```
"""
    return prompt


def _parse_opencode_response(response: str) -> Tuple[int, str]:
    """Parse fit rating and justification from opencode response.

    Args:
        response: Raw response from opencode

    Returns:
        Tuple of (fit_rating, justification)

    Raises:
        ValueError: If response cannot be parsed
        KeyError: If required fields are missing
    """
    # Try to extract JSON from response
    response = response.strip()

    # Handle text ratings like "EXCLUDE", "BACKLOG", "STANDARD", "PRIORITY" or numeric 0-3
    text_rating_map = {
        "exclude": 0,
        "backlog": 1,
        "standard": 2,
        "priority": 3,
    }

    # First try to parse as JSON
    try:
        # Find JSON object in response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Support both old format (fit_rating/composite_fit_rating) and new format (triage_rating)
            # Use explicit None checks because 0 is falsy in Python
            triage = data.get("triage_rating")
            composite = data.get("composite_fit_rating")
            legacy = data.get("fit_rating")
            fit_rating = triage if triage is not None else (composite if composite is not None else legacy)
            justification = data.get("actionable_justification") or data.get("justification") or ""

            # Handle missing fit_rating
            if fit_rating is None:
                raise ValueError("triage_rating not found in response")

            # Handle text rating in JSON (e.g., "EXCLUDE", "PRIORITY")
            if isinstance(fit_rating, str):
                fit_rating_lower = fit_rating.lower().strip()
                if fit_rating_lower in text_rating_map:
                    fit_rating = text_rating_map[fit_rating_lower]
                else:
                    raise ValueError(f"Unknown fit_rating text: {fit_rating}")

            fit_rating = int(fit_rating)

            if fit_rating not in [0, 1, 2, 3]:
                raise ValueError(f"triage_rating must be 0-3, got: {fit_rating}")

            return fit_rating, justification
    except json.JSONDecodeError:
        pass

    # Try to parse text-based response
    response_lower = response.lower()

    # Check for text ratings
    for text, rating in text_rating_map.items():
        if text in response_lower:
            # Extract justification after the rating text
            parts = response.split(text, 1)
            if len(parts) > 1:
                justification = parts[1].strip()
                # Clean up common prefixes
                for prefix in [":", "-", ")", ">", "."]:
                    if justification.startswith(prefix):
                        justification = justification[1:].strip()
                return rating, justification[:200]  # Limit length

    # If no recognized format, raise error
    raise ValueError(f"Unable to parse opencode response: {response[:100]}")


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
