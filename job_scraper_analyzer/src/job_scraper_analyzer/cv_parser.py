"""CV parser to extract plain text for AI context.

Supports both LaTeX (.tex) and YAML-based resume formats.
YAML resumes support three variants: general, systems, infrastructure.
"""

import re
from pathlib import Path
from typing import Any, List, Optional

import yaml

# Pre-compiled regex patterns for LaTeX command stripping
_LATEX_CMD_WITH_BRACES = re.compile(r'\\[a-zA-Z]+\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}')
_LATEX_CMD_WITHOUT_BRACES = re.compile(r'\\[a-zA-Z]+')
_LATEX_NEWCOMMAND_DEF = re.compile(r"\\newcommand\{[^}]*\}\{[^}]*\}")
_LATEX_BEGIN_END = re.compile(r"\\(?:begin|end)\s*\{[^}]*\}")
_WHITESPACE_COLLAPSE = re.compile(r"[ \t]+")
_BLANK_LINES_COLLAPSE = re.compile(r"\n{3,}")
_SKILLSEP_NORMALIZE = re.compile(r"\\skillsep")


def _strip_latex_commands(text: str) -> str:
    """Strip LaTeX commands from text, preserving content in braces.

    Args:
        text: LaTeX text

    Returns:
        Plain text with commands stripped
    """
    # Extract content from all brace groups after a command
    def extract_cmd_content(match: re.Match) -> str:
        full = match.group(0)
        contents = re.findall(r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', full)
        return " ".join(contents)

    # Iteratively strip commands until no change (handles nested commands)
    prev = text
    for _ in range(10):
        text = _LATEX_CMD_WITH_BRACES.sub(extract_cmd_content, text)
        if text == prev:
            break
        prev = text

    # Remove remaining commands without braces
    text = _LATEX_CMD_WITHOUT_BRACES.sub('', text)

    return text


def parse_latex_file(file_path: Path) -> str:
    """Extract plain text from a LaTeX file.

    Strips LaTeX commands and returns human-readable text content.

    Args:
        file_path: Path to the .tex file

    Returns:
        Plain text extracted from the LaTeX file

    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"LaTeX file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        return ""

    # Remove LaTeX comment lines (lines starting with %)
    content = "\n".join(line for line in content.split("\n") if not line.strip().startswith("%"))

    # Remove LaTeX command definitions like \newcommand{\skillsep}{...}
    content = _LATEX_NEWCOMMAND_DEF.sub('', content)

    # Remove skillsep macros and normalize whitespace
    content = _SKILLSEP_NORMALIZE.sub(" | ", content)

    # Strip all LaTeX commands, preserving content in braces
    content = _strip_latex_commands(content)

    # Remove remaining \begin{...} and \end{...} blocks
    content = _LATEX_BEGIN_END.sub('', content)

    # Normalize whitespace: collapse multiple spaces/tabs to single space
    content = _WHITESPACE_COLLAPSE.sub(' ', content)

    # Normalize newlines: collapse multiple blank lines to single newline
    content = _BLANK_LINES_COLLAPSE.sub('\n\n', content)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in content.split("\n")]

    # Filter out empty lines at start/end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines)


def _parse_single_file(tex_file: Path) -> Optional[str]:
    """Parse a single .tex file and return plain text, or None on error.

    Args:
        tex_file: Path to the .tex file

    Returns:
        Plain text content or None if file cannot be read
    """
    try:
        text = parse_latex_file(tex_file)
        return text if text else None
    except (FileNotFoundError, UnicodeDecodeError):
        return None


def parse_cv_directory(cv_dir: Path) -> str:
    """Parse all .tex files in a CV directory and combine their text.

    Args:
        cv_dir: Path to directory containing .tex files

    Returns:
        Combined plain text from all .tex files in the directory

    Raises:
        FileNotFoundError: If the directory does not exist
        NotADirectoryError: If the path is not a directory
    """
    if not cv_dir.exists():
        raise FileNotFoundError(f"CV directory not found: {cv_dir}")

    if not cv_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {cv_dir}")

    # Find all .tex files in the directory
    tex_files = sorted(cv_dir.glob("*.tex"))

    if not tex_files:
        return ""

    # Parse each file and combine results
    results = [
        text for tex_file in tex_files
        if (text := _parse_single_file(tex_file)) is not None
    ]

    # Combine all results with double newline separation
    return "\n\n".join(results)


# Valid resume variants
VALID_VARIANTS = ("general", "systems", "infrastructure")


def _load_yaml(path: Path) -> Any:
    """Load a YAML file and return its contents.

    Args:
        path: Path to the YAML file

    Returns:
        Parsed YAML content (list or dict)

    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the YAML is malformed
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _bullets_for_variant(
    bullets: List[dict],
    variant: str,
) -> List[str]:
    """Filter bullet points that match the given variant.

    Args:
        bullets: List of bullet dicts with 'text' and 'variant' keys
        variant: Target variant ("general", "systems", "infrastructure", or "all")

    Returns:
        List of matching bullet texts
    """
    result = []
    for b in bullets:
        bv = b.get("variant", "")
        if variant == "all" or bv == variant or bv == "shared":
            result.append(b["text"])
    return result


def _build_config_section(config: dict, variant: str) -> List[str]:
    """Build the personal info and summary section from config.yaml.

    Args:
        config: Parsed config.yaml content
        variant: Target variant

    Returns:
        List of text lines for this section
    """
    lines = []
    titles = config.get("title", {})
    summaries = config.get("summary", {})

    if variant == "all":
        for v in VALID_VARIANTS:
            t = titles.get(v, "")
            if t:
                lines.append(f"Title ({v}): {t}")
    else:
        t = titles.get(variant, "")
        if t:
            lines.append(f"Title: {t}")

    if variant == "all":
        lines.append("")
        lines.append("Summaries by variant:")
        for v in VALID_VARIANTS:
            s = summaries.get(v, "")
            if s:
                lines.append(f"  [{v}] {s.strip()}")
    else:
        s = summaries.get(variant, "")
        if s:
            lines.append(f"Summary: {s.strip()}")

    cert = config.get("certification", "")
    if cert:
        lines.append(f"Certification: {cert.strip()}")

    job_target = config.get("job_target")
    if job_target:
        target_text = " ".join(job_target) if isinstance(job_target, list) else str(job_target)
        lines.append(f"Job Target: {target_text.strip()}")

    ai_policy = config.get("ai_policy")
    if ai_policy:
        policy_lines = [p.strip() for p in ai_policy if isinstance(p, str) and p.strip()]
        if policy_lines:
            lines.append("AI Policy:")
            for pl in policy_lines:
                lines.append(f"  - {pl}")

    return lines


def _build_experience_section(experience: list, variant: str) -> List[str]:
    """Build the experience section from experience.yaml.

    Args:
        experience: Parsed experience.yaml content
        variant: Target variant

    Returns:
        List of text lines for this section
    """
    lines = []
    for entry in experience:
        roles = entry.get("role", {})
        company = entry.get("company", "")
        location = entry.get("location", "")
        start = entry.get("start_date", "")
        end = entry.get("end_date") or "Present"

        if variant == "all":
            role_parts = []
            for v in VALID_VARIANTS:
                r = roles.get(v, "")
                if r:
                    role_parts.append(f"{v}: {r}")
            role_str = " | ".join(role_parts)
        else:
            role_str = roles.get(variant, roles.get("general", ""))

        lines.append(f"\n{company} ({location}) — {role_str}")
        lines.append(f"  {start} – {end}")

        bullets = entry.get("bullets", [])
        matching = _bullets_for_variant(bullets, variant)
        for b in matching:
            lines.append(f"  • {b}")

    return lines


def _build_skills_section(skills: list, variant: str) -> List[str]:
    """Build the skills section from skills.yaml.

    Args:
        skills: Parsed skills.yaml content
        variant: Target variant

    Returns:
        List of text lines for this section
    """
    lines = []

    if variant == "all":
        for v in VALID_VARIANTS:
            lines.append(f"\n[{v.title()} Skills]")
            for cat in skills:
                if cat.get("variant") == v:
                    category_name = cat.get("category", "")
                    items = cat.get("items", [])
                    lines.append(f"  {category_name}: {', '.join(items)}")
    else:
        for cat in skills:
            if cat.get("variant") == variant:
                category_name = cat.get("category", "")
                items = cat.get("items", [])
                lines.append(f"  {category_name}: {', '.join(items)}")

    return lines


def _build_education_section(education: list) -> List[str]:
    """Build the education section from education.yaml.

    Args:
        education: Parsed education.yaml content

    Returns:
        List of text lines for this section
    """
    lines = []
    for entry in education:
        degree = entry.get("degree", "")
        institution = entry.get("institution", "")
        end_date = entry.get("end_date", "")
        lines.append(f"{degree} — {institution} ({end_date})")
    return lines


def _build_projects_section(projects: list) -> List[str]:
    """Build the projects section from projects.yaml.

    Args:
        projects: Parsed projects.yaml content

    Returns:
        List of text lines for this section
    """
    lines = []
    for proj in projects:
        name = proj.get("name", "")
        desc = proj.get("description", "")
        techs = proj.get("technologies", [])
        tech_str = ", ".join(techs) if techs else ""
        lines.append(f"\n{name}")
        if desc:
            lines.append(f"  {desc}")
        if tech_str:
            lines.append(f"  Technologies: {tech_str}")
    return lines


def parse_yaml_resume(
    content_dir: Path,
    variant: str = "all",
) -> str:
    """Parse YAML resume files from a content directory and build structured text.

    Reads all YAML files in the content directory and assembles a structured
    plain-text representation of the resume, filtered by variant.

    Args:
        content_dir: Path to the content/ directory containing YAML files
        variant: Resume variant to build ("general", "systems", "infrastructure",
                 or "all" for combined). Defaults to "all".

    Returns:
        Structured plain text representation of the resume

    Raises:
        FileNotFoundError: If the content directory or required YAML files don't exist
        ValueError: If variant is invalid
        yaml.YAMLError: If a YAML file is malformed
    """
    if variant not in ("general", "systems", "infrastructure", "all"):
        raise ValueError(f"Invalid variant '{variant}'. Must be one of: general, systems, infrastructure, all")

    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory not found: {content_dir}")
    if not content_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {content_dir}")

    config = _load_yaml(content_dir / "config.yaml")
    experience = _load_yaml(content_dir / "experience.yaml")
    skills = _load_yaml(content_dir / "skills.yaml")
    education = _load_yaml(content_dir / "education.yaml")
    projects = _load_yaml(content_dir / "projects.yaml")

    sections = []

    # Personal info
    name = config.get("name", "")
    contact = config.get("contact", {})
    location = contact.get("location", "")
    email = contact.get("email", "")
    github = contact.get("github", "")
    website = contact.get("website", "")
    sections.append(f"{name} — {location}")
    sections.append(f"Email: {email} | GitHub: {github} | Website: {website}")

    # Config (title, summary, certification, job target, AI policy)
    sections.extend(_build_config_section(config, variant))

    # Experience
    exp_lines = _build_experience_section(experience, variant)
    if exp_lines:
        sections.append("\nExperience")
        sections.extend(exp_lines)

    # Education
    edu_lines = _build_education_section(education)
    if edu_lines:
        sections.append("\nEducation")
        sections.extend(edu_lines)

    # Skills
    skill_lines = _build_skills_section(skills, variant)
    if skill_lines:
        sections.append("\nSkills")
        sections.extend(skill_lines)

    # Projects
    proj_lines = _build_projects_section(projects)
    if proj_lines:
        sections.append("\nProjects")
        sections.extend(proj_lines)

    return "\n".join(sections)


def extract_cv_summary(text: str, max_length: int = 500) -> str:
    """Extract a summary from CV text, truncating to max_length.

    Truncates at word boundaries to avoid cutting words in the middle.

    Args:
        text: The full CV text
        max_length: Maximum length of the returned summary (default: 500)

    Returns:
        Truncated text that fits within max_length characters
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    # Find the last space before max_length to avoid cutting words
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space > max_length * 0.8:
        # If space is found and it's not too far back, cut there
        return truncated[:last_space].strip()
    else:
        # Otherwise just cut at max_length
        return truncated.strip()
