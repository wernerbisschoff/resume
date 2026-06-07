# Explore: YAML Content Layer Migration

> **Epic:** 002-yaml-content-layer
> **Scan date:** 2026-06-07
> **Scanner:** deviate-explore (Codebase Scanner + Ecosystem Researcher)

---

## [PROBLEM_DEFINITION]

**Statement:** Replace the current hardcoded `content/data.typ` + `content/master-list.md` duality with a single YAML-based canonical content layer that both Typst (CV PDF, 3 variants) and Astro (website) consume.

**Scope:** Structural components verified across the scan:
- `content/data.typ` — 298-line hardcoded data dictionary (experience, education, skills, projects, config, cover letter)
- `content/master-list.md` — per-variant bullet text with STAR cross-references
- `content/star-stories.md` — 14 full STAR-format stories
- `lib/template.typ` — layout engine consuming data.typ exports via `_resolve()` / `_resolve_entries()`
- `cv.typ`, `cv_systems.typ`, `cv_infrastructure.typ`, `cover_letter.typ` — entry points
- `specs/constitution.md` — governance artifact (architectural principles, tech stack, testing, DoD)
- Ecosystem: Typst 0.14.2 built-in `yaml()` function (no external package needed)

**Exclusions:**
- Architectural decisions, design trade-offs, or risk analysis — deferred to `deviate-research`
- Data modeling (YAML schema design) — deferred to `deviate-research`
- Failure-mode speculation — deferred to `deviate-research`
- Implementation code generation — out of scope for this phase

---

## [DISCOVERY_AUDIT_RESULTS]

### Manifest Files Observed

| Manifest | Description |
|----------|-------------|
| `.mise.toml` | Tool version manager: `typst = "0.14.2"`, 13 task definitions (build, check, lint, dev, clean, setup, help) |
| `.github/workflows/release.yml` | GitHub Actions CI/CD — matrix build of 4 entry points on `v*.*.*` tag push, font install, artifact upload, GH Release |
| `lib/lang.toml` | i18n localization strings for resume/cover letter across 10 languages |
| `.gitignore` | Excludes build/, logs, .typst/, PDFs, .worktrees/ |

### Verified Dependencies

| Dependency | Declared In | Version |
|------------|-------------|---------|
| `typst` | `.mise.toml` | `0.14.2` |
| `@preview/linguify:0.5.0` | `lib/modern-cv.typ` line 1 | `0.5.0` |
| `typst-community/setup-typst@v5` | `.github/workflows/release.yml` | `@v5` |
| `actions/checkout` | `.github/workflows/release.yml` | `@v4` |
| `actions/upload-artifact` | `.github/workflows/release.yml` | `@v4` |
| `actions/download-artifact` | `.github/workflows/release.yml` | `@v4` |
| `softprops/action-gh-release` | `.github/workflows/release.yml` | `@v2` |
| Font files | `fonts/` directory | Roboto (8), Source Sans 3 (15), FontAwesome (1) |

### Ghost Dependencies

| Reference | Location | Issue |
|-----------|----------|-------|
| `@preview/yaml:0.2.0` | `content/yaml-content-migration-spec.md` line 603 | **Does not exist** on Typst universe (404). Typst 0.14.2 has built-in `yaml()` — no package needed. |
| `typst check` command | `specs/constitution.md` line 49, `.mise.toml` line 35 | Referenced by constitution but **no `.mise.toml` task invokes `typst check`** — only `typst compile` and `typst fmt --check` are wired. |
| `typst fmt --check` | `specs/constitution.md` line 50, `.mise.toml` line 38 | `.mise.toml` `[tasks.lint]` runs `typst compile` (compilation check) rather than `typst fmt --check`. |
| "Source Sans Pro" font name | `lib/modern-cv.typ` lines 388, 750 | Legacy name — current fonts are "Source Sans 3". May cause fallback resolution failures in some environments. |

### Test Runner Configuration

| Source | Command |
|--------|---------|
| `.mise.toml` task `check` | `typst compile --font-path fonts cv.typ W_Bisschoff_CV.pdf && typst compile --font-path fonts cv_systems.typ W_Bisschoff_CV_systems.pdf && typst compile --font-path fonts cv_infrastructure.typ W_Bisschoff_CV_infrastructure.pdf && typst compile --font-path fonts cover_letter.typ W_Bisschoff_Cover_Letter.pdf` |
| `.mise.toml` task `lint` | `typst compile --font-path fonts cv.typ /dev/null && typst compile --font-path fonts cover_letter.typ /dev/null` |
| `specs/constitution.md` (declared) | `typst compile {entry}.typ {entry}.pdf` (test) + `typst fmt --check` (lint) |

### Manifest-Constitution Divergence

**⚠ CONFLICT — YAML Serialization Ban vs YAML Migration Spec**

Constitution `specs/constitution.md` line 13:
```
- **Minimal Complexity**: No external JSON/YAML data serialization — native Typst dictionaries only.
```

Constitution `specs/constitution.md` line 14:
```
- **Deterministic Builds**: Zero external network calls during compilation.
```

Migration spec `content/yaml-content-migration-spec.md` (via `content/yaml-content-migration-spec.md` lines 4-6):
> Goal: Replace the current hardcoded `content/data.typ` + `content/master-list.md` duality with a single YAML-based canonical content layer.

Migration spec architecture diagram (lines 782-811): Central `content/*.yaml` as canonical source of truth.

The constitution at line 13 explicitly prohibits external YAML/JSON serialization and mandates "native Typst dictionaries only." The migration spec proposes exactly what the constitution bans. Additionally, the earlier design doc at `specs/001-typst-cv-migration/design.md` explicitly rejected YAML/JSON:
> Option C: External JSON/YAML Data Serialization... Rejected because it over-engineers... violates the mandate for minimum code

**Note**: The migration spec at `content/yaml-content-migration-spec.md` references `@preview/yaml:0.2.0` (line 603), but this package **does not exist** on the Typst universe. Typst 0.14.2 has a built-in `yaml()` function, so no external package or network call is needed for YAML parsing. The technical objection (network call during compilation, line 14) can be satisfied with built-in `yaml()`, but the constitutional objection at line 13 (ban on YAML serialization itself) remains unresolved.

---

## [CONSTITUTION_QUOTES]

Verbatim from `specs/constitution.md`:

- **Architectural Principles**:
  > 8: - **LaTeX Removal**: All LaTeX artifacts (`.tex`, `.cls`, LaTeX-specific Dockerfiles, VS Code LaTeX configs) must be removed.
  > 9: - **Data/Presentation Separation**: Content must be strictly separated from layout logic using native Typst dictionaries.
  > 10: - **ATS Compatibility**: All resumes must use single-column layout and `#set text(ligatures: false)` globally.
  > 11: - **Bi-Variant Output**: System must support at least three resume variants (General, Embedded Systems Engineer, Enterprise/Infrastructure Engineer) and corresponding cover letters.
  > 12: - **Font Management**: Custom fonts must be explicitly loaded via `#set text(font: "...")` using Typst-native equivalents or vendored files for deterministic rendering.
  > 13: - **Minimal Complexity**: No external JSON/YAML data serialization — native Typst dictionaries only.
  > 14: - **Deterministic Builds**: Zero external network calls during compilation.

- **Tech Stack Standards**:
  > 16: ## Tech Stack Standards
  > 17: ### Backend
  > 18: - None (static document generation only)
  > 19:
  > 20: ### Frontend
  > 21: - None (PDF output only)
  > 22:
  > 23: ### Database
  > 24: - None
  > 25:
  > 26: ### Infrastructure
  > 27: - **CI/CD**: GitHub Actions (Ubuntu runner)
  > 28: - **Compilation**: `typst-community/setup-typst@v5` with matrix strategy for variant compilation
  > 29: - **Release**: `softprops/action-gh-release@v2` for PDF asset publishing
  > 30: - **Trigger**: Git tag push (semver `v*` or calver `YYYY.MM*`)
  > 31:
  > 32: ### Tooling
  > 33: - **Language**: Typst (latest stable)
  > 34: - **Formatter**: `typst fmt --check`
  > 35: - **Type Checker**: `typst check`
  > 36: - **Compiler**: `typst compile`

- **Testing Protocols**:
  > 38: ## Testing Protocols
  > 39: ### Framework
  > 40: - `TEST_FRAMEWORK`: typst
  > 41: - `TEST_ROOT`: none
  > 42: - `TEST_EXT`: none
  > 43: - `TEST_COMMAND`: typst compile {entry}.typ {entry}.pdf
  > 44: - `LINT_COMMAND`: typst fmt --check
  > 45:
  > 46: ### Coverage
  > 47: - No coverage framework applicable (static document generation)
  > 48: - Compilation success is the primary test
  > 49: - `typst check` must pass on all `.typ` files
  > 50: - `typst fmt --check` must pass to ensure consistent code style

- **Definition of Done**:
  > 52: ## Definition of Done
  > 53: - [ ] Code implemented per functional requirements
  > 54: - [ ] `typst compile` succeeds on all variant entry points
  > 55: - [ ] `typst check` passes on all `.typ` files
  > 56: - [ ] `typst fmt --check` passes
  > 57: - [ ] PDF output is single-column with `ligatures: false`
  > 58: - [ ] CI pipeline compiles and releases all variants on tag push
  > 59: - [ ] All LaTeX artifacts removed (unless flagged for user decision)
  > 60: - [ ] No governance violations

---

## [ARCHITECTURAL_BASELINES]

### Existing Architectural Patterns

**Entry point routing:**
```
cv.typ ──imports──> content/data.typ ──imports──> lib/template.typ ──imports──> lib/modern-cv.typ
                       exports cv_data                        exports render_cv()
```

`cv.typ` entry point (4 lines):
```typst
#import "content/data.typ": cv_data
#import "lib/template.typ": render_cv
#render_cv(cv_data, variant: "general")
```

Variant entry points filter experience and override position:
```typst
#let filtered_experience = cv_data.experience.filter(entry =>
  entry.variant_tags.contains("systems")
)
#let variant_data = cv_data + (
  position: "Hybrid Edge/Systems Engineer",
  experience: filtered_experience,
  experience_entries: filtered_experience,
)
#render_cv(variant_data, variant: "systems")
```

**Variant resolution pattern** in `lib/template.typ`:
```typst
#let _resolve(value, variant) = {
  if type(value) == dictionary and variant in value {
    value.at(variant)
  } else {
    value
  }
}

#let _resolve_entries(entries, variant) = {
  entries.map(entry => (
    role: _resolve(entry.at("role", default: "Role"), variant),
    company: entry.at("company", default: ""),
    description: _resolve(entry.at("description", default: ()), variant),
  ))
}
```

### Infrastructure & Operations

**CI/CD** (`.github/workflows/release.yml`):
```yaml
name: Release CV
on:
  push:
    tags:
      - "v*.*.*"
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        entry:
          - source: cv.typ
            output: W_Bisschoff_CV.pdf
          - source: cv_systems.typ
            output: W_Bisschoff_CV_systems.pdf
```

**Mise tooling** (`.mise.toml`):
```toml
[tools]
typst = "0.14.2"

[tasks.check-compile]
description = "Verify all documents compile without errors"
run = "typst compile --font-path fonts cv.typ W_Bisschoff_CV.pdf && ..."
```

### Data & State Management

**Current data model** in `content/data.typ` — variant-aware dictionaries with all variants' data in one structure:
```typst
#let _experience_entries = (
  (
    role: (
      general: "Founder and Host",
      systems: "Principal Systems Architect",
      infrastructure: "Principal Systems Architect",
    ),
    company: "Divergent Tabletop",
    variant_tags: ("general", "systems", "infrastructure"),
    description: (
      general: ([Founded neurodivergent-focused peer community...],),
      systems: ([Engineered a distributed real-time data engine...],),
      infrastructure: ([Implemented a single-database multi-tenant...],),
    ),
  ),
)
```

`cv_data` export shape (keys consumed by template):
```typst
#let cv_data = (
  name, email, phone, location, github, website, linkedin,
  position: (general: "...", systems: "...", infrastructure: "..."),
  summary: (general: "...", systems: "...", infrastructure: "..."),
  certification, ai_policy, job_target,
  experience: _experience_entries,
  education: _education_entries,
  skills: _skill_categories,
  projects: _project_entries,
)
```

### Quality, Safety & Observability

**Testing**: Compilation success is the primary test. No unit test framework.

```toml
[tasks.check]
description = "Run all verification checks (compile)"
depends = ["check-compile"]
```

`mise run check` compiles all 4 entry points sequentially. Visual verification required for layout shifts.

**No `typst check` or `typst fmt --check` tasks are wired** in `.mise.toml` despite being declared in the constitution.

### External Integrations

| Integration | Source | Purpose |
|-------------|--------|---------|
| `@preview/linguify:0.5.0` | Typst universe | i18n for resume/cover letter strings |
| `lib/modern-cv.typ` | Vendored (third-party, modified) | Awesome CV Typst port — `resume()`, `coverletter()` helpers |
| `fonts/` | Vendored .ttf files | Roboto + Source Sans 3 + FontAwesome |
| GitHub Actions | `typst-community/setup-typst@v5` | CI compilation environment |

---

## [ECOSYSTEM_RESEARCH]

### Best Practices

**YAML import in Typst is built-in (no third-party package needed).** The `@preview/yaml` package does not exist on Typst universe (confirmed 404). Starting from Typst 0.3.0+, a built-in `yaml()` function is available in the standard library.

Usage (Typst 0.12+):
```typst
#let data = yaml("path/to/file.yaml")
```

Source: https://typst.app/docs/reference/data-loading/yaml/

Data-in-YAML, layout-in-Typst pattern is demonstrated in official docs:
```typst
#let bookshelf(contents) = {
  for (author, works) in contents {
    author
    for work in works [
      - #work.title (#work.published)
    ]
  }
}
#bookshelf(yaml("scifi-authors.yaml"))
```

### Common Use Cases & Pitfalls

| Issue | Detail |
|-------|--------|
| **Null handling** | YAML `null` → Typst `none`. Must use `.at(key, default: ...)` or explicit `if` checks. |
| **Integer overflow** | YAML integers > 2^63-1 become `float` (precision loss). |
| **Custom YAML tags ignored** | `!tag` values are loaded without tag semantics. |
| **File paths relative** | YAML paths in `yaml()` are relative to the calling Typst file's directory. |
| **No schema validation** | Missing keys cause runtime errors — defensive `.at(key, default:)` essential. |
| **Nested data access** | YAML nested mappings → nested Typst dictionaries. Access with `.key` or `.at("key")`. |
| **Built-in formats** | Typst has built-in support for JSON, TOML, CBOR, XML, CSV, and YAML equally. |

### Standard Tooling

- **Current stable Typst**: 0.14.2
- **YAML API** (built-in, no package):
  - `yaml(path)` — reads from file path (str) or raw YAML bytes
  - `yaml.encode(value)` — encodes Typst data to YAML string
- **Conversion**: YAML null→`none`, boolean→`bool`, number→`int`/`float`, string→`str`, sequence→`array`, mapping→`dictionary`
- **Filtering pattern for CV variants**: `.filter(r => r.variant == "systems" and r.priority <= 2)` works natively on YAML-imported data

Source: https://typst.app/docs/reference/data-loading/yaml/#conversion

---

## [FILE_REGISTRY]

| Path (Strictly Relative to Repo Root) | Type | Purpose | Verbatim Snippet (≤10 lines) |
| :--- | :--- | :--- | :--- |
| `content/data.typ` | Typst source | Hardcoded data dictionary — target of migration | `#let _experience_entries = (` |
| `content/master-list.md` | Markdown | Per-variant bullet text with STAR cross-refs | `# Experience Master — Werner Bisschoff` |
| `content/star-stories.md` | Markdown | 14 full STAR-format stories | `# Amazon LP Cheatsheet — Draft` |
| `content/yaml-content-migration-spec.md` | Markdown | Migration spec: YAML canonical layer proposal | `# YAML Content Layer — Migration Spec` |
| `content/website-rework-handover.md` | Markdown | Website content handover analysis | `# Website Rework — Content Handover` |
| `lib/template.typ` | Typst source | Layout engine — render_cv(), _resolve(), _resolve_entries() | `#let _resolve(value, variant) = {` |
| `lib/modern-cv.typ` | Typst source | Third-party Awesome CV Typst port (995 lines) | `#import "@preview/linguify:0.5.0": *` |
| `lib/lang.toml` | TOML | i18n strings (10 languages) | `[conf]` |
| `cv.typ` | Typst source | Entry point — general variant | `#render_cv(cv_data, variant: "general")` |
| `cv_systems.typ` | Typst source | Entry point — systems variant | `#let filtered_experience = cv_data.experience.filter(entry =>` |
| `cv_infrastructure.typ` | Typst source | Entry point — infrastructure variant | `#let filtered_experience = cv_data.experience.filter(entry =>` |
| `cv_embedded.typ` | Typst source | Deprecated entry point (broken — filters for "embedded") | `#import "content/data.typ": cv_data` |
| `cv_enterprise.typ` | Typst source | Deprecated entry point (broken — filters for "enterprise") | `#import "content/data.typ": cv_data` |
| `cover_letter.typ` | Typst source | Entry point — cover letter (variant: "general") | `#import "content/data.typ": cv_data` |
| `.mise.toml` | Manifest | Tooling config: typst 0.14.2, build/check/lint tasks | `[tools]` |
| `.github/workflows/release.yml` | CI/CD Config | GitHub Actions — matrix build on tag push | `name: Release CV` |
| `.gitignore` | Config | Ignore patterns | `build/` |
| `specs/constitution.md` | Governance | Architectural principles, tech stack, testing, DoD | `# Project Constitution` |
| `specs/issues.jsonl` | Issues Ledger | Issue tracking — ISS-001, ISS-002 completed; 002 epic in BACKLOG | `{"issue_id":"ISS-001","type":"feature","title":"Local...` |
| `specs/001-typst-cv-migration/design.md` | Design Doc | Multi-entry modular architecture design | `# Design: Typst CV Migration` |
| `specs/001-typst-cv-migration/data-model.md` | Data Model Doc | CVData, ExperienceEntry, EducationEntry models | `# Data Model: Typst CV Migration` |
| `specs/002-yaml-content-layer/` | Directory | Feature bucket (empty — target for explore.md) | (empty) |
| `AGENTS.md` | Agent Config | Agent instructions — data/layout separation, verification | `# AGENTS.md` |
| `MEMORY.md` | Session Memory | Variant rename decisions, session state | `# Session Memory — June 2026` |
| `CLAUDE.md` | Project Config | Entry points, variant profiles, ATS guards | `# CLAUDE.md — latex-cv / Typst Migration` |
| `fonts/` | Font Directory | 25 font files (Roboto, Source Sans 3, FontAwesome) | `FontAwesome.ttf` |
| `img/` | Image Directory | Profile pictures | `profile.jpg` |

---

## [STATUS_SUMMARY]

| Metric | Value |
| :--- | :--- |
| STATUS | SUCCESS |
| FEATURE_SLUG | 002-yaml-content-layer |
| GIT_BRANCH | main |
| SPEC_TARGET | specs/002-yaml-content-layer/explore.md |
| EPIC_ID | 002 |
| NEXT_ACTION | Run the `deviate-research` skill |
