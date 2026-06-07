# Website Rework — Content Handover

> **Source:** Analysis of werner.bisschoff.dev (current) vs. CV master-list + STAR stories (content/star-stories.md)
> **Goal:** Transform the site from a general portfolio into a STAR-driven, impact-rich narrative.
> **Date:** 2026-06-07

---

## Current Site Structure (Astro 5.0 / Tailwind / DaisyUI / Cloudflare)

- **Home:** Hero + LLM-Accelerated Development (3 cards) + 4 Philosophy Pillars + Background narrative
- **Work:** 4 case studies (FSM, Workflow Modernization, Testing Infrastructure, Portfolio Site)
- **Resume:** (placeholder? I couldn't access it behind authwall)
- **Contact:** contact@bisschoff.dev + GitHub + LinkedIn links

---

## What's Missing From the Site

### 1. Divergent Tabletop — Entirely Absent
This is your **current, active role** (Jul 2025–Present) and your most architecturally sophisticated work. The site mentions zero of it:
- Elixir/OTP + CRDT real-time wiki engine (Kintree)
- Rust-backed y_ex synchronization layer (sub-50ms convergence)
- PostgreSQL RLS multi-tenant architecture
- 85% write reduction via GenServer buffer flushing
- Spec-Driven Development (SDD) methodology
- Divergent Tabletop community website (Astro/WCAG)

**This should be the hero case study.** It's the most technically impressive and most recent.

### 2. STAR Stories / Metrics — Entirely Absent
The site describes what you did but never with STAR structure or measurable outcomes. The CV master-list and star-stories.md have 14 fully written STAR stories. The site needs:

- **SOME/IP Performance Investigation** (STAR 1) — 80% latency improvement via perf/flamegraphs
- **Docker Dev Container** (STAR 2) — setup time hours → <1 hour
- **SOME/IP Hardware Mocks** (STAR 3) — adopted by team, CI-integrated
- **IPC Service Implementation** (STAR 4) — sole ownership end-to-end
- **FSM Framework** (STAR 5) — customer built products on top of it
- **WBUS3 Protocol** (STAR 6) — I2C + testing framework
- **NFC/E-ink Label App** (STAR 7) — reverse engineered proprietary protocol
- **Testing Framework at FARO** (STAR 8) — no allocated time, built anyway
- **UX Improvements at FARO** (STAR 9) — pushed back on "training gap" framing
- **SDD Framework** (STAR 10) — own development methodology
- **Kintree CRDT Architecture** (STAR 11) — zero lock conflicts
- **Self-taught Elixir/Phoenix** (STAR 12) — production-grade from scratch
- **Events Rotation System** (STAR 13) — solved multi-table hosting solo
- **Divergent Tabletop Website** (STAR 14) — WCAG + forced-scroll trigger warnings

**Action:** Convert the case studies page to STAR format. Add 2–3 more case studies (SOME/IP perf, Docker dev container, FSM Framework).

### 3. Spec-Driven Development (SDD) — Not Mentioned
The CV's AI policy section and SDD framework are a key differentiator:
- "Treat AI as an agentic partner within a strict engineering framework"
- Spec-Driven Development > vibe coding
- Bullet points: data security, engineering rigour, privacy by design

**Action:** Add an SDD / AI Methodology section to the home page or a dedicated page.

### 4. Skills — No Dedicated Section
The CV has organised skill categories (Primary, Secondary, Foundational, Other). The site has none.

**Action:** Add a skills matrix (even collapsed) — valuable for keyword matching and recruiter scanning.

### 5. AWS Certification In Progress
Listed in CV (`AWS Certified Solutions Architect – Associate (In Progress — Target: 6 Weeks)`) — not on site.

### 6. How I Work / Engineering Philosophy
The current site has 4 pillars (Build Safety Nets, Remove Friction, Design for Maintainability, Balance Speed with Quality) which are good but generic. The CV's "how I work" section is more specific:
- "I approach software through the lens of Spec-Driven Development (SDD)"
- AI-augmented methodology with guardrails

### 7. Cover Letter / About Me Positioning
The cover letter data in data.typ has strong positioning text that could be adapted for the site:
- "Bridging hardware, full-stack development, and resilient system architecture"
- "Deep technical expertise with a rigorous, AI-augmented methodology"
- "I don't just write code; I design systems that last"

---

## Suggested Rework Plan (Priority Order)

### Phase 1: Content Enrichment (No Structural Changes)
1. Add metrics to existing case studies (pull from STAR stories)
2. Add STAR-format snippets to job descriptions on home page
3. Add Divergent Tabletop to the job timeline (most important gap)
4. Add SDD/AI Methodology section

### Phase 2: New Sections
5. Dedicated Skills page/section
6. Expand case studies from 4 → 6 (add SOME/IP perf, FSM Framework)
7. Add certification + AWS badge

### Phase 3: Structural
8. Consider reworking the home page narrative to lead with impact metrics
9. Resume page — make sure it links to or embeds the Typst PDF

---

## Cross-Reference: STAR Stories → Site Location

| STAR # | Title | Should Go On |
|--------|-------|--------------|
| 1 | SOME/IP Performance Investigation | Work page (new case study) |
| 2 | Docker Development Container | Work page (new case study) |
| 3 | SOME/IP Hardware Mocks | Work / UMAN section |
| 4 | IPC Service Implementation | Work / UMAN section |
| 5 | FSM Framework | Work page (expand existing case study with metrics) |
| 6 | WBUS3 Protocol | Work / Ingenics section |
| 7 | NFC/E-ink Label App | Work / FARO section |
| 8 | Testing Framework at FARO | Work page (expand existing with STAR detail) |
| 9 | UX Improvements at FARO | Work / FARO section |
| 10 | SDD Framework | Home (new AI Methodology section) |
| 11 | Kintree CRDT Architecture | Work page (new case study, Divergent Tabletop) |
| 12 | Self-taught Elixir/Phoenix | Work / Divergent Tabletop section |
| 13 | Events Rotation System | Work / Divergent Tabletop section |
| 14 | Divergent Tabletop Website | Work / Divergent Tabletop section |

---

## Reference Files in This Repo

| File | Content |
|------|---------|
| `content/star-stories.md` | 14 full STAR stories in Amazon LP format |
| `content/master-list.md` | Canonical experience entries with STAR cross-refs |
| `content/data.typ` | Typst CV content (3 variants: general / systems / infrastructure) |
| `amazon-lp-cheatsheet-draft.md` | LP-indexed story index with quick picks |
| `W_Bisschoff_CV_infrastructure.pdf` | Example compiled CV PDF |
