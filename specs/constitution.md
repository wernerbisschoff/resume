# Project Constitution

**Version:** 0.3.0

---

## Architectural Principles
- **LaTeX Removal**: All LaTeX artifacts (`.tex`, `.cls`, LaTeX-specific Dockerfiles, VS Code LaTeX configs) must be removed.
- **Data/Presentation Separation**: Content must be strictly separated from layout logic — stored in `content/*.yaml`, consumed via Typst's built-in `yaml()`.
- **ATS Compatibility**: All resumes must use single-column layout and `#set text(ligatures: false)` globally.
- **Bi-Variant Output**: System must support at least three resume variants (General, Embedded Systems Engineer, Enterprise/Infrastructure Engineer) and corresponding cover letters.
- **Font Management**: Custom fonts must be explicitly loaded via `#set text(font: "...")` using Typst-native equivalents or vendored files for deterministic rendering.
- **Canonical Data Source**: YAML (`content/*.yaml`) is the single source of truth — imported via Typst's built-in `yaml()`. No external packages required.
- **Deterministic Builds**: Zero external network calls during compilation.

## Tech Stack Standards
### Backend
- None (static document generation only)

### Frontend
- None (PDF output only)

### Database
- None

### Infrastructure
- **CI/CD**: GitHub Actions (Ubuntu runner)
- **Compilation**: `typst-community/setup-typst@v5` with matrix strategy for variant compilation
- **Release**: `softprops/action-gh-release@v2` for PDF asset publishing
- **Trigger**: Git tag push (semver `v*` or calver `YYYY.MM*`)

### Tooling
- **Language**: Typst 0.14.2 (pinned via `.mise.toml`)
- **YAML Validator**: `yamllint` (run via `mise run check-yaml`)
- **Compiler**: `typst compile`
- **Task Runner**: `mise` (orchestrates compile, lint, test)

## Testing Protocols
### Framework
- `TEST_FRAMEWORK`: Shell (bash) + Typst compile check
- `TEST_ROOT`: tests/
- `TEST_EXT`: .sh
- `TEST_COMMAND`: mise run test
- `LINT_COMMAND`: mise run check-yaml

### Coverage
- No coverage framework applicable (static document generation)
- Compilation success is the primary test
- `yamllint content/*.yaml` must pass with no errors (warnings tolerated)
- `mise run check` must pass — validates YAML and compiles all entry points

## Definition of Done
- [ ] Code implemented per functional requirements
- [ ] `typst compile` succeeds on all variant entry points
- [ ] `mise run check` passes
- [ ] PDF output is single-column with `ligatures: false`
- [ ] CI pipeline compiles and releases all variants on tag push
- [ ] All LaTeX artifacts removed (unless flagged for user decision)
- [ ] No governance violations

## Version History
- 0.1.0 — Initial constitution from Typst CV Migration (explore/design/prd)
- 0.2.0 — Replaced YAML ban with YAML canonical data source; updated Data/Presentation Separation to reference `content/*.yaml`
- 0.3.0 — Updated tooling for Typst 0.14.2 (removed `typst fmt --check`/`typst check` which are unavailable); replaced with `yamllint` + `mise run check`
