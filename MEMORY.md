# Session Memory — June 2026

## CV Rework — Phase 1

### What changed

- **Variant rename**: `embedded` → `systems`, `enterprise` → `infrastructure`. This was a global rename across `data.typ` (variant keys, variant_tags, dictionary keys), variant files, `.mise.toml`, `.github/workflows/release.yml`, and `analysis/experience_master.md`.
- **New files**: `cv_systems.typ` and `cv_infrastructure.typ` are the active entry points. Old `cv_embedded.typ` / `cv_enterprise.typ` are deprecated and broken (filter for old variant keys).
- **Output PDFs**: `W_Bisschoff_CV_systems.pdf` and `W_Bisschoff_CV_infrastructure.pdf`.

### Skills section

| Change | Detail |
|--------|--------|
| **Position** | Moved from bottom to directly beneath Summary (top-third) |
| **Format** | Grid columns replaced with inline `Category : Value1, Value2` (ATS-safe) |
| **Systems categories** | Primary Competencies, Secondary Competencies, Foundational Systems, Cross-Domain Integration |
| **Infrastructure categories** | Primary Competencies, Secondary Platforms, Data Layer Infrastructure, Systems & Automation |
| **SDD added** | Spec-Driven Development added to both variants (fits on 1 page) |

### Content reframes

| Entry | Systems | Infrastructure |
|-------|---------|---------------|
| Divergent Tabletop | Rewritten as STAR bullets (CRDT, GenServer buffers, BEAM supervision) | Kept original PostgreSQL/RLS/Oban focus |
| FARO Africa (bullet 4) | Kept original | Replaced AWS/Pulumi with Vultr Linux infra reframe |
| Junior Lecturer | Removed | Removed (page space) |

### Key decisions

- Expo/React Native intentionally excluded from infrastructure CV (prevents front-end ATS classification)
- Technical Application Scope section removed entirely (was padding)
- Certification marker added as separate header line
- Pulumi moved from Primary to Systems & Automation (infrastructure CV)
- Python and PostgreSQL promoted to Primary (infrastructure CV)

### Things to watch

- If adding content, check `pdfinfo` page count — both variants must stay on 1 page
- Skills section uses inline format — verify with `pdftotext -layout` that categories render on same line as values
- Cover letter uses `variant: "general"` — unaffected by the rename
- The `position` field in variant files overrides `data.typ` — keep them in sync

## Head of Systems Variant — July 2026

Temporary CV/cover letter pair targeting a Head of Systems role (game lodge group, Sabi Sands, Sea Point office). Application pack uses generic employer references — no company name in either document.

### What changed

- **New variant**: `head_of_systems`. Added to `_variants` tuple in `data.typ` (cap=2 like systems/infrastructure).
- **Entry points**: `cv_head_of_systems.typ` and `cover_letter_head_of_systems.typ`.
- **Output PDFs**: `W_Bisschoff_CV_head_of_systems.pdf` (1 page) and `W_Bisschoff_Cover_Letter_head_of_systems.pdf` (1 page).
- **CV title**: "Systems & Infrastructure Engineer | Business Systems, Process Improvement, Integrations, Reporting" — reflects the candidate's current role rather than the target Head of Systems title.
- **CV header (this variant)**: certification suppressed via `cv_data + (certification: none)` in the entry point. Location retained. Suppressed because "AWS Certified Solutions Architect – In Progress" is recruiter-facing, not relevant to a lodge operator audience.
- **Skills trimmed**: category names shortened ("Automation", "Reporting", "Infrastructure", "Stakeholders") and items shortened ("Workflow config", "Systems admin", "User access", "Process automation", "BI reports", "Management reports", "Linux admin", "Security & access", "User support", "Cross-functional work") so each row fits on a single line.
- **Summary trimmed**: 5 sentences → 3 sentences for tighter top-of-page.
- **Bullets trimmed**: Ingenics Digital and UMAN Technologies reduced to 1 bullet each for the head_of_systems variant only (the others still have 2).
- **Skills items font size**: 11pt → 10pt (`resume-skill-values` in `lib/modern-cv.typ`) so skills text matches the body text used by experience bullets and summary. Affects all variants — no layout regressions.

### Skills categories

Business systems, Automation, Reporting, Infrastructure, Stakeholders.

### Experience reframes

- **FARO Africa**: rewritten to foreground ERPNext/Frappe customisation, UX-led process improvement, reporting, Linux infrastructure with Docker Compose, and translating operational pain points into systems changes. Role title: "Full-Stack ERPNext Automation Engineer".
- **Divergent Tabletop**: rewritten to foreground founder-level ownership, accessibility-aware system design, and resilient backend/data systems. Role title: "Founder / Principal Systems Architect". The shared "Elixir/OTP/CRDT" bullet still appears (technical detail preserved for other variants).
- **Ingenics Digital & UMAN Technologies**: 1 bullet each in this variant, reframed around business-systems tooling. Role titles: "Embedded Tooling & Automation Engineer" / "Software & Tooling Developer".

### Cover letter

- 1 page, ~220 words, 6 short sections.
- ADHD-friendly structure: short paragraphs, clear role statement upfront, concrete examples (FARO, ERPNext, Divergent Tabletop), plain language, active voice.
- Company-agnostic — no Tengile/MalaMala references in either CV or cover letter.
- "Job Application for [position]" header reads the candidate's current title (Systems & Infrastructure Engineer | …).

### Things to watch

- The Divergent Tabletop `shared` bullet ("Elixir/OTP/CRDTs…") still appears here. Acceptable per user spec ("specialised runtime language unless directly relevant to a specific achievement") since it carries the 85% DB write reduction metric. If revisited, change `variant: shared` to a list and update `_bullets_for_variant` in `data.typ`.
- Branch: `feat/001-typst-cv-migration/head-of-systems-variant`. Per AGENTS.md scope convention for Typst migration work.
- 1-page constraint applies to both CV and cover letter for this variant.
