# Constitution

This document defines the architectural standards, tech stack constraints, testing mandates, and completion criteria for the `latex-cv` repository migration to Typst.

## [Language]
Typst

## [Dependencies]
- `typst` (binary, latest stable)
- `typst-community/setup-typst@v5` (GitHub Action for CI/CD)

## [Testing]
Static document generation verification. No unit testing framework is required. Compilation success is the primary test.

## [Runtime]
- Local: Typst CLI
- CI: GitHub Actions (Ubuntu runner)

## [Constraints]
1. **LaTeX Removal**: All LaTeX artifacts (`.tex`, `.cls`, LaTeX-specific Dockerfiles, LaTeX VS Code tasks) must be removed.
2. **Data/Presentation Separation**: Content must be separated from layout logic (e.g., using Typst imports or data files).
3. **ATS Compatibility**: Resumes must use a single-column layout and `ligatures: false` on `set text()`.
4. **Bi-Variant Output**: The system must support at least two resume variants (Systems Engineer, Enterprise/Infrastructure Engineer) and corresponding cover letters.
5. **Font Management**: Custom fonts (e.g., Roboto, FontAwesome) must be explicitly loaded and vendored if required, or replaced with Typst-native equivalents.

## [Test]
typst compile main.typ main.pdf

## [Lint]
typst fmt --check

## [TypeCheck]
typst check main.typ
