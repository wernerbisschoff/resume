---
title: "Local Typst CV Generation Engine"
labels: ["feature", "typst", "core"]
source_file: "specs/001-typst-cv-migration/prd.md"
blocked_by: []
coordinates_with: []
issue_id: "ISS-001"
---

## [SYSTEM_TOPOLOGY_MAPPING]
- **Epic Domain**: 001-typst-cv-migration
- **Local File Paths**: 
  - `content/data.typ`
  - `lib/template.typ`
  - `cv.typ`
  - `cv_embedded.typ`
  - `cv_enterprise.typ`
  - `cover_letter.typ`
- **Workstation Paths**: Local Typst CLI environment.

## [THE_PROBLEM_CONTRACT]
As a user, I need a local, functional Typst-based CV generation system that separates data from layout and produces ATS-compatible PDFs for multiple variants (general, embedded, enterprise) and cover letters, without relying on any CI/CD pipeline or legacy LaTeX files.

## [SCOPE_BOUNDARIES]
- **Hard Inclusions**: 
  - Implement `content/data.typ` with centralized dictionaries.
  - Implement `lib/template.typ` enforcing `ligatures: false` and single-column layout.
  - Create variant entry points (`cv.typ`, `cv_embedded.typ`, `cv_enterprise.typ`, `cover_letter.typ`).
- **Defensive Exclusions**: 
  - Do NOT modify `.github/workflows/release.yml` yet.
  - Do NOT delete any `.tex` or `.cls` files yet (deferred to ISS-002).

## [UPSTREAM_REQUIREMENT_TRACING]
- **FR-001-DATA**: Centralized Data Dictionary
  - `AC-001-DATA-01`, `AC-001-DATA-02`
- **FR-002-LAYOUT**: Pure Layout Engine
  - `AC-002-LAYOUT-01`, `AC-002-LAYOUT-02`
- **FR-003-ENTRY**: Variant Entry Point Orchestration
  - `AC-003-ENTRY-01`, `AC-003-ENTRY-02`

## [MULTI_TIERED_VERIFICATION_TARGETS]
- **Unit/Static**: `typst check content/data.typ`, `typst fmt --check lib/template.typ`
- **Integration**: `typst compile cv.typ cv.pdf`, `typst compile cv_embedded.typ cv_embedded.pdf`

## [DEMONSTRATION_PATH]
```bash
# 1. Validate syntax and formatting
typst check content/data.typ
typst fmt --check lib/template.typ

# 2. Compile all variants locally to verify end-to-end generation
typst compile cv.typ cv.pdf
typst compile cv_embedded.typ cv_embedded.pdf
typst compile cv_enterprise.typ cv_enterprise.pdf
typst compile cover_letter.typ cover_letter.pdf

# 3. Verify PDFs exist and are non-empty
ls -lh *.pdf
```