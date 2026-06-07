---
title: "feat(002): Legacy Artifact Removal & CI Verification"
labels:
  - "epic:002-yaml-content-layer"
  - "type:feature"
source_file: "specs/002-yaml-content-layer/prd.md"
blocked_by:
  - "ISS-001"
coordinates_with: []
issue_id: "ISS-002"
---

## [SYSTEM_TOPOLOGY_MAPPING]

- **Epic Domain**: `002-yaml-content-layer`
- **Local Issue Path**: `specs/002-yaml-content-layer/issues/002-legacy-cleanup-ci-verification.md`
- **Workstation Paths** (relative to repo root):
  - `content/master-list.md` (delete)
  - `content/star-stories.md` (evaluate for deletion — superseded by `content/star-stories.yaml`)
  - `.github/workflows/release.yml` (verify/update)
  - `.mise.toml` (verify task definitions)

## [THE_PROBLEM_CONTRACT]

After ISS-001 establishes the YAML-driven compilation pipeline, legacy artifacts remain in the repository:

1. `content/master-list.md` — superseded by `content/experience.yaml` + `content/star-stories.yaml`
2. `content/star-stories.md` — superseded by `content/star-stories.yaml`
3. CI pipeline may reference legacy file paths or lack YAML-aware validation

This issue delivers the final cleanup: legacy files are removed, the CI pipeline is verified to compile all variants using the new YAML adapter layer, and deterministic build invariants are confirmed. After this issue, the repository contains zero legacy data sources and the CI pipeline validates the complete YAML architecture.

## [SCOPE_BOUNDARIES]

### Hard Inclusions

1. **Delete `content/master-list.md`** — fully superseded by YAML canonical data layer
2. **Evaluate and delete `content/star-stories.md`** — superseded by `content/star-stories.yaml`; retain only if it contains data not yet migrated to YAML
3. **Verify CI pipeline** (`.github/workflows/release.yml`):
   - Confirms all variant entry points compile via `typst compile --font-path fonts`
   - No external network calls during compilation (deterministic build mandate)
   - Matrix strategy covers all CV variants
4. **Verify `mise run check`** passes for all entry points after legacy file removal
5. **Confirm no dangling references** — grep codebase for imports/references to deleted files

### Defensive Exclusions

- Do NOT modify YAML files created in ISS-001
- Do NOT modify `content/data.typ` adapter logic (completed in ISS-001)
- Do NOT modify `lib/template.typ` rendering logic (completed in ISS-001)
- Do NOT implement automated YAML schema validation tooling (out of scope)
- Do NOT introduce new CI steps beyond verifying existing compilation pipeline
- Do NOT delete `content/yaml-content-migration-spec.md` or `content/website-rework-handover.md` (not legacy data sources)

## [UPSTREAM_REQUIREMENT_TRACING]

| Token | Source | Description |
| :--- | :--- | :--- |
| FR-004-LEGACY-CLEANUP | `prd.md` | Artifact removal and CI verification |
| AC-004-01 | `prd.md` | master-list.md removed, mise run check passes for all 4 entry points |
| AC-004-02 | `prd.md` | CI pipeline compiles all variants using YAML adapter, no external network calls |

## [MULTI_TIERED_VERIFICATION_TARGETS]

### Unit-Level (Per-File)

- `content/master-list.md` does not exist after deletion
- `content/star-stories.md` does not exist (if deleted) or contains a migration note
- No `.typ` file imports or references deleted files

### Integration-Level (Cross-File)

- `mise run check` passes — all 4 entry points compile successfully
- `typst fmt --check` passes on all `.typ` files
- No dangling `#include` or `yaml()` references to deleted files
- CI workflow compiles all variants without errors

## [DEMONSTRATION_PATH]

```bash
# 1. Verify legacy files are removed
test ! -f content/master-list.md && echo "PASS: master-list.md removed"

# 2. Check for dangling references to deleted files
grep -r "master-list" content/ lib/ *.typ || echo "PASS: no dangling references"
grep -r "star-stories.md" content/ lib/ *.typ || echo "PASS: no star-stories.md references"

# 3. Full compilation check via mise
mise run check

# 4. Verify formatting on all Typst files
typst fmt --check content/data.typ
typst fmt --check lib/template.typ
typst fmt --check lib/modern-cv.typ

# 5. Verify CI workflow references correct paths
grep -A5 "typst compile" .github/workflows/release.yml

# 6. Confirm deterministic builds (no network calls)
grep -r "http" content/*.yaml lib/*.typ || echo "PASS: no network references"
```
