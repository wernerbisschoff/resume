---
title: "Automated Release Pipeline and Legacy Cleanup"
labels: ["feature", "ci-cd", "cleanup"]
source_file: "specs/001-typst-cv-migration/prd.md"
blocked_by: ["ISS-001"]
coordinates_with: []
issue_id: "ISS-002"
---

## [SYSTEM_TOPOLOGY_MAPPING]
- **Epic Domain**: 001-typst-cv-migration
- **Local File Paths**: 
  - `.github/workflows/release.yml`
  - `.gitignore`
  - Legacy files to remove: `*.tex`, `*.cls`, `docker/`, `.vscode/`, `.devcontainer/`
- **Workstation Paths**: GitHub Actions (Ubuntu runner), Local Git CLI.

## [THE_PROBLEM_CONTRACT]
As a maintainer, I need the Typst CV generation to be fully automated via GitHub Actions on tag pushes, and I need all legacy LaTeX artifacts and configurations removed from the repository to prevent build confusion and scope creep, ensuring a clean, Typst-only codebase.

## [SCOPE_BOUNDARIES]
- **Hard Inclusions**: 
  - Migrate `.github/workflows/release.yml` to use `typst-community/setup-typst@v5` with a matrix strategy.
  - Update `.gitignore` to exclude Typst cache/build artifacts.
  - Remove all `.tex`, `.cls`, `docker/Dockerfile`, `docker/build.sh`, `.devcontainer/*`, `.vscode/*`.
- **Defensive Exclusions**: 
  - Do NOT modify `content/data.typ` or `lib/template.typ` (owned by ISS-001).
  - Do NOT auto-delete advisory files (`analysis/`, `amazon-lp-cheatsheet-draft.md`) without explicit user confirmation.

## [UPSTREAM_REQUIREMENT_TRACING]
- **FR-004-CI**: GitHub Actions Pipeline Migration
  - `AC-004-CI-01`, `AC-004-CI-02`
- **FR-005-CLEANUP**: LaTeX Artifact Removal
  - `AC-005-CLEANUP-01`, `AC-005-CLEANUP-02`

## [MULTI_TIERED_VERIFICATION_TARGETS]
- **Static**: `find . -name "*.tex" -o -name "*.cls" | grep -v "example/" | wc -l` (should return 0)
- **Integration**: Push a test tag (e.g., `v0.0.1-test`) and verify GitHub Actions matrix build succeeds and releases artifacts.

## [DEMONSTRATION_PATH]
```bash
# 1. Verify legacy LaTeX files are removed (excluding example/ if retained for reference)
find . -name "*.tex" -o -name "*.cls" | grep -v "example/" | wc -l
# Expected output: 0

# 2. Verify CI workflow uses the correct Typst action
cat .github/workflows/release.yml | grep "typst-community/setup-typst@v5"

# 3. Verify .gitignore is updated for Typst artifacts
cat .gitignore | grep ".typst/"
```