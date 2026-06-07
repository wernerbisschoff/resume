---
title: "feat(002): YAML-Driven CV Compilation Pipeline"
labels:
  - "epic:002-yaml-content-layer"
  - "type:feature"
source_file: "specs/002-yaml-content-layer/prd.md"
blocked_by: []
coordinates_with: []
issue_id: "ISS-001"
---

## [SYSTEM_TOPOLOGY_MAPPING]

- **Epic Domain**: `002-yaml-content-layer`
- **Local Issue Path**: `specs/002-yaml-content-layer/issues/001-yaml-driven-cv-compilation.md`
- **Workstation Paths** (relative to repo root):
  - `content/config.yaml` (create)
  - `content/experience.yaml` (create)
  - `content/star-stories.yaml` (create)
  - `content/skills.yaml` (create)
  - `content/projects.yaml` (create)
  - `content/education.yaml` (create)
  - `content/data.typ` (rewrite)
  - `lib/template.typ` (modify)
  - `cv.typ` (verify only)
  - `cv_systems.typ` (verify only)
  - `cv_infrastructure.typ` (verify only)
  - `cv_embedded.typ` (verify only)
  - `cv_enterprise.typ` (verify only)

## [THE_PROBLEM_CONTRACT]

The current CV system uses a 298-line hardcoded Typst dictionary (`content/data.typ`) and a supplementary markdown file (`content/master-list.md`) as dual data sources. This architecture prevents:

1. **Unified consumption** — A future Astro website cannot import Typst dictionary literals.
2. **Explicit curation** — No metadata exists to control which bullets appear on which CV variant vs. the website.
3. **STAR story linking** — No structured mechanism to link experience bullets to detailed STAR stories.

This issue delivers the complete vertical pipeline: canonical YAML files are created, a thin Typst adapter imports them via the built-in `yaml()` function, and the template engine consumes the adapted data to produce valid PDFs. After this issue, `typst compile cv.typ W_Bisschoff_CV.pdf` produces a PDF sourced entirely from YAML.

## [SCOPE_BOUNDARIES]

### Hard Inclusions

1. **Create 6 canonical YAML files** in `content/`:
   - `config.yaml` — personal info, contact, summary (schema per `data-model.md` §Config)
   - `experience.yaml` — all roles with bullets tagged `cv_priority` ∈ {1,2,3}, `website_show` ∈ {true,false}, `star_ref` ∈ string|null (schema per `data-model.md` §Experience)
   - `star-stories.yaml` — all STAR stories with unique `id` slugs (schema per `data-model.md` §StarStory)
   - `skills.yaml` — categorized skill lists (schema per `data-model.md` §Skill)
   - `projects.yaml` — projects with `cv_priority` and `website_show` tags (schema per `data-model.md` §Project)
   - `education.yaml` — education entries with `cv_priority` (schema per `data-model.md` §Education)

2. **Rewrite `content/data.typ`** as a thin YAML import adapter:
   - Use Typst's built-in `yaml()` function (NOT `@preview/yaml` — strictly forbidden per constitution)
   - Export a `cv_data` dictionary compatible with `lib/template.typ`'s existing `render_cv(cv_data, variant: "...")` signature
   - Use `.at(key, default: ...)` for ALL nested YAML access to prevent runtime crashes from missing keys
   - Implement variant filtering: bullets where `cv_priority <= max_priority_for_variant`
   - Implement `star_ref` resolution: lookup in `star-stories.yaml`, graceful degradation if `null`

3. **Update `lib/template.typ`** to consume YAML-derived data:
   - Preserve existing `render_cv()` entry point signature
   - Ensure all data access uses defensive `.at(key, default:)` patterns
   - Remove any remaining hardcoded data references
   - Ensure `star_ref` resolution renders STAR story details or degrades gracefully

### Defensive Exclusions

- Do NOT delete `content/master-list.md` (deferred to ISS-002)
- Do NOT modify `.github/workflows/release.yml` (deferred to ISS-002)
- Do NOT implement Astro website integration (out of scope for this epic)
- Do NOT introduce external YAML preprocessing scripts (violates deterministic build mandate)
- Do NOT use `@preview/yaml` or any external package (constitution forbids it)
- Do NOT add automated YAML schema validation tooling (mitigated via manual assertions)

## [UPSTREAM_REQUIREMENT_TRACING]

| Token | Source | Description |
| :--- | :--- | :--- |
| FR-001-YAML-DATA-LAYER | `prd.md` | Canonical YAML data creation — 6 files with curation metadata |
| FR-002-TYPST-ADAPTER | `prd.md` | Typst YAML import layer — thin adapter replacing hardcoded data.typ |
| FR-003-TEMPLATE-ALIGNMENT | `prd.md` | Template engine compatibility — lib/template.typ consumes YAML-derived data |
| AC-001-01 | `prd.md` | All 6 YAML files exist with 100% legacy data, bullets tagged with cv_priority and website_show |
| AC-001-02 | `prd.md` | experience.yaml passes yamllint validation |
| AC-002-01 | `prd.md` | typst compile cv.typ succeeds, PDF visually matches baseline |
| AC-002-02 | `prd.md` | typst compile cv_systems.typ succeeds with variant filtering (cv_priority <= 2) |
| AC-003-01 | `prd.md` | typst fmt --check passes on lib/template.typ, no legacy hardcoded references |
| AC-003-02 | `prd.md` | star_ref resolution works — STAR story details appended or graceful degradation |

## [MULTI_TIERED_VERIFICATION_TARGETS]

### Unit-Level (Per-File)

- Each YAML file passes `yamllint` without errors
- `content/data.typ` exports `cv_data` without runtime errors
- `lib/template.typ` passes `typst fmt --check`

### Integration-Level (Cross-File)

- `typst compile --font-path fonts cv.typ W_Bisschoff_CV.pdf` succeeds
- `typst compile --font-path fonts cv_systems.typ W_Bisschoff_CV_systems.pdf` succeeds with correct variant filtering
- `typst compile --font-path fonts cv_infrastructure.typ W_Bisschoff_CV_infrastructure.pdf` succeeds
- `typst compile --font-path fonts cover_letter.typ W_Bisschoff_Cover_Letter.pdf` succeeds
- `star_ref` links resolve correctly in PDF output (visual verification)

## [DEMONSTRATION_PATH]

```bash
# 1. Verify all 6 YAML files exist
ls content/config.yaml content/experience.yaml content/star-stories.yaml content/skills.yaml content/projects.yaml content/education.yaml

# 2. Verify YAML syntax (requires yamllint: pip install yamllint)
yamllint content/*.yaml

# 3. Verify cv_priority and website_show tags present on experience bullets
grep -c "cv_priority" content/experience.yaml
grep -c "website_show" content/experience.yaml

# 4. Compile general CV — must succeed without errors
typst compile --font-path fonts cv.typ W_Bisschoff_CV.pdf

# 5. Compile systems CV — must filter by variant (cv_priority <= 2)
typst compile --font-path fonts cv_systems.typ W_Bisschoff_CV_systems.pdf

# 6. Compile infrastructure CV
typst compile --font-path fonts cv_infrastructure.typ W_Bisschoff_CV_infrastructure.pdf

# 7. Compile cover letter
typst compile --font-path fonts cover_letter.typ W_Bisschoff_Cover_Letter.pdf

# 8. Verify formatting
typst fmt --check lib/template.typ
typst fmt --check content/data.typ

# 9. Full check suite
mise run check
```
