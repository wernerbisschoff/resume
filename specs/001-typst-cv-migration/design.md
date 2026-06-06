# Design: Typst CV Migration

## [RECOMMENDED_ARCHITECTURE]
**Multi-Entry Point Modular Architecture**

This approach directly maps to the existing architectural baselines ("Three root CV entry points... Three cover letter entry points") while leveraging Typst's native module system for strict constitutional compliance ("Data/Presentation Separation: Content must be separated from layout logic").

**Module Surface:**
- **Add**: `content/data.typ` (centralized dictionary of all professional experience, education, and skills), `lib/template.typ` (pure layout engine enforcing ATS compatibility), `cv.typ`, `cv_embedded.typ`, `cv_enterprise.typ`, `cover_letter.typ` (variant entry points).
- **Modify**: `.github/workflows/release.yml` (replace `xu-cheng/latex-action@v3` with `typst-community/setup-typst@v5`), `.gitignore` (update to exclude Typst cache/build artifacts).
- **Remove**: All `.tex` files, `awesome-cv.cls`, `docker/Dockerfile`, `docker/build.sh`, `.devcontainer/*`, `.vscode/*` (LaTeX-specific configurations).

**Rationale:**
This option satisfies all constitutional constraints without introducing external build dependencies. It achieves identical data separation to JSON/YAML approaches but uses native Typst dictionaries, ensuring perfect type-checking via `typst check` and zero build-step overhead. It maintains a 1:1 mapping to the legacy `FILE_REGISTRY` structure, ensuring high reversibility and low blast radius during the migration phase.

## [OPTIONS_MATRIX]
| Option | Complexity | Testability | Constitutional Alignment | Reversibility | Blast Radius | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Option A: Multi-Entry Modular | Low | High | Aligned | High | Low | Recommended |
| Option B: Monolithic CLI-Driven | Medium | Medium | Tension | High | Medium | Rejected |
| Option C: External JSON/YAML Parsing | High | Low | Tension | Low | High | Rejected |

## [REJECTED_OPTIONS]
- **Option B: Monolithic CLI-Driven Compilation**: A single `main.typ` file driven by environment variables or CLI arguments. Rejected because it violates the principle of minimal complexity, complicates the GitHub Actions runtime configuration, and makes isolated test execution ambiguous without wrapper scripts.
- **Option C: External JSON/YAML Data Serialization**: Storing content in `.json` or `.yaml` and using Typst's `read()` or a pre-processor. Rejected because it over-engineers the "YAML/JSON data separation" best practice, introducing unnecessary fragility and violating the mandate for minimum code that solves the problem.

## [DESIGN_TRADEOFFS]
| Decision | Trade-off | Why This Side |
| :--- | :--- | :--- |
| Data Serialization Format | Native Typst Dict vs. JSON | Native dictionaries offer perfect type-checking via `typst check` and zero build-step overhead, satisfying Data/Presentation Separation without violating simplicity mandates. |
| Font Management | System fonts vs. Bundled fonts | Explicitly loading fonts via `#set text(font: "...")` using Typst-native equivalents (e.g., "Linux Libertine") ensures deterministic rendering across local and CI environments, meeting the Font Management constraint. |
| CI/CD Granularity | Single compilation step vs. Matrix build | Using a GitHub Actions matrix strategy over distinct entry points ensures that a failure in one variant's compilation does not silently skip the others, maximizing test reliability. |

## [CONTRARIAN_VIEWPOINTS]
- **Multi-Entry Point Modular Architecture**: A single entry point (`main.typ`) driven by a configuration dictionary reduces CI matrix complexity and prevents drift between entry points. Multiple entry points multiply the surface area for build configuration errors.
- **Centralized Dictionary**: A monolithic `content/data.typ` file becomes a merge-conflict magnet and violates the Single Responsibility Principle as the CV grows. A modular data topology (e.g., `content/experience.typ`, `content/education.typ`) provides better git diff granularity.
- **Pure Layout Logic**: Over-abstracting layout into a generic `lib/template.typ` can lead to a leaky abstraction where the file becomes bloated with variant-specific conditional logic, effectively recreating the tangled LaTeX macro hell the migration aims to escape.

## [RISK_REGISTER]
| Risk ID | Risk | Likelihood | Impact | Mitigation | Owner | Source Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| RSK-001 | Silent data omission due to missing dictionary keys | Medium | High | Implement strict validation helper functions in `lib/template.typ` that assert key presence before rendering. | Template Engine | `explore.md:173` |
| RSK-002 | CI build failure due to missing custom fonts on Ubuntu runner | Medium | High | Bundle required `.ttf`/`.otf` files in the repository or configure `setup-typst` to install them explicitly. | CI/CD Pipeline | `explore.md:147` |
| RSK-003 | Localized overrides accidentally re-enable ligatures, breaking ATS compatibility | Low | High | Enforce `#set text(ligatures: false)` at the root of every entry point file and audit with a post-compilation text extraction script. | Template Engine | `explore.md:131` |

## [CONSTITUTIONAL_ALIGNMENT_AUDIT]
| Constitutional Clause | Architectural Decision | Alignment | Notes |
| :--- | :--- | :--- | :--- |
| [Constraint] 1. LaTeX Removal | Migration to `.typ` files; removal of `.tex`/`.cls`/Dockerfiles. | Aligned | Directly satisfies the mandate to eliminate all LaTeX artifacts. |
| [Constraint] 2. Data/Presentation Separation | `content/data.typ` (data) + `lib/template.typ` (layout). | Aligned | Enforces strict boundary between content dictionary and rendering logic. |
| [Constraint] 3. ATS Compatibility | Single-column layout, `ligatures: false`. | Tension | Requires diligent global enforcement; Typst's defaults or localized overrides can easily introduce subtle violations. |
| [Constraint] 4. Bi-Variant Output | Variant entry points (`cv.typ`, `cv_embedded.typ`, `cv_enterprise.typ`). | Aligned | Explicitly supports multiple resume variants and cover letters via distinct compilation targets. |
| [Constraint] 5. Font Management | Custom fonts explicitly loaded or replaced with native equivalents. | Tension | Bundling fonts bloats git history; relying on system fonts in CI is fragile without explicit installation steps. |
| [Test] Static compilation | `typst compile main.typ main.pdf` | Aligned | Standard Typst compilation command validates document generation. |
| [Lint] Formatting | `typst fmt --check` | Aligned | Native Typst formatter ensures consistent code style. |
| [TypeCheck] Static analysis | `typst check main.typ` | Aligned | Native Typst type checker validates syntax and basic type constraints before compilation. |

## [SOURCE_REGISTRY]
| ID | Type | Source / Path (Strictly Relative to Repo Root) | Relevance Note |
| :--- | :--- | :--- | :--- |
| SRC-001 | Explore_MD | `specs/001-typst-cv-migration/explore.md` | Primary factual context for file registry, baselines, and ecosystem research. |
| SRC-002 | Constitution | `specs/constitution.md` | Bootstrapped architectural constraints and testing mandates. |
| SRC-003 | Industry_Baseline | `https://github.com/typst-community/setup-typst` | Recommended GitHub Action for flexible, caching-supported Typst CI/CD. |

## [STATUS_SUMMARY]
| Metric | Value |
| :--- | :--- |
| STATUS | AWAITING_HITL_GATE_1 |
| FEATURE_SLUG | 001-typst-cv-migration |
| EPIC_ID | 001 |
| GIT_BRANCH | main |
| SPEC_TARGET_DESIGN | `specs/001-typst-cv-migration/design.md` |
| SPEC_TARGET_DATAMODEL | `specs/001-typst-cv-migration/data-model.md` |
| NEXT_ACTION | Human reviews design.md + data-model.md, then invokes the `prd` skill |
