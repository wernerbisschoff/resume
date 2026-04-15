"""LaTeX CV parser to extract plain text for AI context."""

import re
from pathlib import Path
from typing import Optional


def _extract_braces_content(text: str) -> str:
    """Extract content from outermost braces, handling nesting.
    
    Args:
        text: Text like {content {nested} here}
        
    Returns:
        Content with outer braces removed: content {nested} here
    """
    if not text.startswith("{"):
        return text
    
    # Find matching closing brace
    depth = 0
    for i, char in enumerate(text):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[1:i]
    
    return text[1:-1] if len(text) > 1 else ""


def _strip_latex_commands(text: str) -> str:
    """Strip LaTeX commands from text, preserving content in braces.
    
    Args:
        text: LaTeX text
        
    Returns:
        Plain text with commands stripped
    """
    # Helper to extract content from braces after a command
    def extract_cmd_content(match):
        # match is like \command{content} or \command{content}{more}
        # We want to extract content from all brace groups
        full = match.group(0)
        # Find all {content} groups and concatenate
        contents = re.findall(r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', full)
        return " ".join(contents)
    
    # Process text iteratively until no more commands
    prev = text
    max_iterations = 10
    for _ in range(max_iterations):
        # Handle \command{arg1}{arg2}... patterns - extract all content
        text = re.sub(
            r'\\[a-zA-Z]+\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
            extract_cmd_content,
            text
        )
        if text == prev:
            break
        prev = text
    
    # Remove any remaining \command patterns without braces
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
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
    
    # Remove LaTeX command definitions like \newcommand{\skillsep}{...}
    content = re.sub(r"\\newcommand\{[^}]*\}\{[^}]*\}", "", content)
    
    # Remove skillsep macros and normalize whitespace
    content = re.sub(r"\\skillsep", " | ", content)
    
    # Strip all LaTeX commands, preserving content in braces
    content = _strip_latex_commands(content)
    
    # Remove remaining \begin{...} and \end{...} blocks (already stripped by _strip_latex_commands)
    content = re.sub(r"\\begin\s*\{[^}]*\}", "", content)
    content = re.sub(r"\\end\s*\{[^}]*\}", "", content)
    
    # Normalize whitespace: collapse multiple spaces/tabs to single space
    content = re.sub(r"[ \t]+", " ", content)
    
    # Normalize newlines: collapse multiple blank lines to single newline
    content = re.sub(r"\n{3,}", "\n\n", content)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in content.split("\n")]
    
    # Filter out empty lines at start/end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return "\n".join(lines)


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
    results = []
    for tex_file in tex_files:
        try:
            text = parse_latex_file(tex_file)
            if text:
                results.append(text)
        except (FileNotFoundError, UnicodeDecodeError):
            # Skip files that can't be read
            continue
    
    # Combine all results with double newline separation
    return "\n\n".join(results)


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
