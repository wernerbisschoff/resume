# Data Model: Typst CV Migration

## [ENTITY_DEFINITIONS]

### `CVData`
- **Source-of-truth**: `content/data.typ`
- **Lifecycle owner**: Centralized data dictionary
- **Attributes**:
  | Attribute | Type | Invariant | Source Anchor |
  | :--- | :--- | :--- | :--- |
  | `name` | `string` | Invariant as "Werner Bisschoff" | `explore.md:201` |
  | `email` | `string` | Valid email format | `explore.md:201` |
  | `phone` | `string` | Valid phone format | `explore.md:201` |
  | `location` | `string` | Non-empty | `explore.md:201` |
  | `position` | `string` | Must match bi-variant targets | `explore.md:202` |
  | `summary` | `content` | Non-empty | `explore.md:205` |
  | `experience` | `array<dictionary>` | ≥1 entry | `explore.md:206` |
  | `education` | `array<dictionary>` | ≥1 entry | `explore.md:207` |
  | `projects` | `array<dictionary>` | ≥0 entries | `explore.md:208` |
  | `skills` | `array<dictionary>` | ≥1 category | `explore.md:209` |
  | `ai_policy` | `content` | Non-empty | `explore.md:210` |
  | `job_target` | `content` | Non-empty | `explore.md:211` |
- **Invariants**: `position` must strictly match one of the bi-variant targets ("Embedded Systems & Real-Time Software Engineer" or "Enterprise Systems & Automation Architect").

### `ExperienceEntry`
- **Source-of-truth**: `analysis/experience_master.md`
- **Lifecycle owner**: Centralized data dictionary
- **Attributes**:
  | Attribute | Type | Invariant | Source Anchor |
  | :--- | :--- | :--- | :--- |
  | `role` | `string` | Non-empty | `explore.md:206` |
  | `company` | `string` | Non-empty | `explore.md:206` |
  | `location` | `string` | Non-empty | `explore.md:206` |
  | `start_date` | `string` | Chronologically before `end_date` | `explore.md:206` |
  | `end_date` | `string \| none` | Valid date or `none` | `explore.md:206` |
  | `description` | `array<content>` | ≥1 bullet point | `explore.md:206` |
  | `variant_tags` | `array<string>` | Subset of `("general", "embedded", "enterprise")` | `explore.md:213` |

### `EducationEntry`
- **Source-of-truth**: `cv/education.tex`, `cv/embedded/education.tex`, `cv/enterprise/education.tex`
- **Lifecycle owner**: Centralized data dictionary
- **Attributes**:
  | Attribute | Type | Invariant | Source Anchor |
  | :--- | :--- | :--- | :--- |
  | `degree` | `string` | Non-empty | `explore.md:207` |
  | `institution` | `string` | Non-empty | `explore.md:207` |
  | `location` | `string` | Non-empty | `explore.md:207` |
  | `graduation_year` | `string` | Valid 4-digit numeric string | `explore.md:207` |
  | `details` | `array<content>` | ≥0 bullet points | `explore.md:207` |

### `SkillCategory`
- **Source-of-truth**: `cv/skills.tex`, `cv/embedded/skills.tex`, `cv/enterprise/skills.tex`
- **Lifecycle owner**: Centralized data dictionary
- **Attributes**:
  | Attribute | Type | Invariant | Source Anchor |
  | :--- | :--- | :--- | :--- |
  | `category_name` | `string` | Unique within variant scope | `explore.md:209` |
  | `skills` | `array<string>` | Non-empty | `explore.md:209` |
  | `variant` | `string` | Matches entry point variant | `explore.md:216` |

### `CoverLetterData`
- **Source-of-truth**: `W_Bisschoff_Cover_Letter.tex` and variants
- **Lifecycle owner**: Centralized data dictionary
- **Attributes**:
  | Attribute | Type | Invariant | Source Anchor |
  | :--- | :--- | :--- | :--- |
  | `recipient_name` | `string` | Non-empty | `explore.md:220` |
  | `recipient_title` | `string` | Non-empty | `explore.md:220` |
  | `company` | `string` | Non-empty | `explore.md:220` |
  | `date` | `string` | Valid date format | `explore.md:220` |
  | `about_me` | `content` | Non-empty | `explore.md:220` |
  | `why_me` | `content` | Non-empty | `explore.md:220` |
  | `variant` | `string` | Aligns with CV variant | `explore.md:221` |

## [RELATIONSHIP_GRAPH]
| From | Relationship | To | Cardinality | On-Delete | On-Cascade | Source Anchor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CVData` | contains | `ExperienceEntry` | 1:N | Cascade | Cascade | `explore.md:201` |
| `CVData` | contains | `EducationEntry` | 1:N | Cascade | Cascade | `explore.md:207` |
| `CVData` | contains | `SkillCategory` | 1:N | Cascade | Cascade | `explore.md:209` |
| `CVData` | pairs with | `CoverLetterData` | 1:1 (per variant) | Restrict | None | `explore.md:78` |

## [SCHEMA_TABLES]

### `content/data.typ`
```typst
#let cv_data = (
  name: "Werner Bisschoff",
  email: "werner@example.com",
  phone: "+27 00 000 0000",
  location: "Cape Town, South Africa",
  position: "Systems Engineer", // Overridden by entry points
  summary: [Software engineer with 5+ years of experience...],
  experience: experience_entries,
  education: education_entries,
  projects: project_entries,
  skills: skill_categories,
  ai_policy: [I treat AI as an agentic partner within a strict engineering framework...],
  job_target: [Seeking a mid to senior software engineering role...],
)

#let experience_entries = (
  (
    role: "Founder and Host",
    company: "Divergent Tabletop",
    location: "Cape Town",
    start_date: "Jul 2025",
    end_date: none,
    description: (
      [Bullet point 1],
      [Bullet point 2],
    ),
    variant_tags: ("embedded", "enterprise"),
  ),
)

#let education_entries = (
  (
    degree: "B.Eng. Computer and Electronic Engineering",
    institution: "North-West University",
    location: "Potchefstroom",
    graduation_year: "2020",
    details: (
      [Project bullet point],
    ),
  ),
)

#let skill_categories = (
  (
    category_name: "Systems Architecture",
    skills: ("Event-driven FSM", "RPC/IPC", "State machines", "Node trees"),
    variant: "general",
  ),
)

#let cover_letter_data = (
  recipient_name: "Hiring Manager",
  recipient_title: "Engineering Lead",
  company: "Target Company",
  date: "2024-01-01",
  about_me: [About me content...],
  why_me: [Why me content...],
  variant: "embedded",
)
```

## [STATE_TRANSITIONS]

### Document Compilation State Machine
- **States**: `Draft`, `Variant_Selected`, `Data_Merged`, `Compiled`, `Released`
- **Initial State**: `Draft`
- **Terminal States**: `Compiled`, `Released`
- **Transitions**:
  | From | Event | Guard | To | Side Effects |
  | :--- | :--- | :--- | :--- | :--- |
  | `Draft` | Invoke entry point | Variant tag matches scope | `Variant_Selected` | Loads specific `.typ` root |
  | `Variant_Selected` | Import data | Data dictionary is valid | `Data_Merged` | Applies ATS constraints (`ligatures: false`) |
  | `Data_Merged` | Execute compiler | Zero syntax/type errors | `Compiled` | Generates clean, single-column PDF |
  | `Compiled` | Git tag push | Tag matches semver/calver | `Released` | GitHub Actions publishes PDF asset |

## [DATA_FLOW]

### Flow: CV Generation Pipeline
1. **Source**: `content/data.typ` acts as the single, centralized source of truth for all personal, professional, and variant-specific data.
2. **Transformation**: `lib/template.typ` acts as a pure layout engine. It receives data dictionaries and applies ATS-compatible formatting rules (e.g., `#set page(margin: (0.5in))`, `#set text(ligatures: false)`).
3. **Orchestration**: Entry point files (`cv.typ`, `cv_embedded.typ`, `cv_enterprise.typ`, `cover_letter.typ`) import both `content/data.typ` and `lib/template.typ`. They inject variant-specific overrides before passing the finalized dictionary to the template functions.
4. **Output**: The Typst compiler generates clean, single-column PDF assets.
5. **Distribution**: GitHub Actions (`.github/workflows/release.yml`) detects version tags, compiles the variants using `typst-community/setup-typst@v5`, and attaches the resulting PDFs to a GitHub Release.

## [SOURCE_REGISTRY]
| ID | Type | Source / Path (Strictly Relative to Repo Root) | Relevance Note |
| :--- | :--- | :--- | :--- |
| SRC-001 | Explore_MD | `specs/001-typst-cv-migration/explore.md` | Primary factual context for file registry and ecosystem research. |
| SRC-002 | Constitution | `specs/constitution.md` | Bootstrapped architectural constraints and testing mandates. |
| SRC-003 | Codebase_File | `analysis/experience_master.md` | Canonical source of truth for all employment experience data. |
