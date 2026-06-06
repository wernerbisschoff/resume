# Exploration: Typst CV Migration

## [PROBLEM_DEFINITION]

[Statement]: Convert the existing LaTeX-based CV repository (`latex-cv`) to a Typst-based system. Remove all LaTeX artifacts. Replace the GitHub Actions CI pipeline to compile Typst source files and release PDFs as downloadable assets. The output should include bi-variant resume targeting (Systems Engineer / Infrastructure Engineer) plus cover letters, all in Typst.

[Scope]: Structural inventory of the entire repository at commit time on branch `main`. Cataloging all file types, build infrastructure, CI/CD pipeline, content sections, and non-CV artifacts.

[Exclusions]: No architectural decisions, design trade-offs, risk analysis, data modeling, or failure-mode speculation — all deferred to the `deviate-research` skill.

---

## [DISCOVERY_AUDIT_RESULTS]

### Verified Dependencies

No manifest-based dependency declarations exist in this repository. There is no `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `mix.exs`, or similar manifest. The build toolchain is entirely environment-managed via Docker images (`texlive/texlive:latest`).

### Ghost Dependencies

- **Awesome-CV LaTeX class**: The file `awesome-cv.cls` is vendored (sourced from `https://github.com/posquit0/Awesome-CV`) and referenced by all `.tex` entry points via `\documentclass[11pt, a4paper]{awesome-cv}`. Not declared in any manifest — vendored directly.
- **LaTeX Workshop VS Code extension**: Referenced in `.vscode/extensions.json` (`James-Yu.latex-workshop`) but not managed by any package manager.
- **GitHub CLI (`gh`)**: Installed via `apt-get` in `.devcontainer/Dockerfile` and `.devcontainer/postCreateCommand.sh` but absent from any lockfile.
- **Starship prompt**: Installed via `curl | sh` in `.devcontainer/postCreateCommand.sh` — no manifest tracking.

### Manifest Files Observed

No standard language/framework manifests exist. Configuration is spread across:

- `.github/workflows/release.yml` — GitHub Actions CI pipeline
- `.devcontainer/devcontainer.json` — VS Code Dev Container configuration
- `.devcontainer/Dockerfile` — Docker image definition for dev environment
- `docker/Dockerfile` — Docker image for production builds
- `.vscode/settings.json` — VS Code editor settings for LaTeX Workshop
- `.vscode/tasks.json` — VS Code task definitions for build/watch/clean
- `.vscode/extensions.json` — Recommended VS Code extensions
- `.gitignore` — Git exclusion rules

### Test Runner Configuration

No test framework or test runner exists anywhere in the repository. Zero test files found.

---

## [CONSTITUTION_QUOTES]

[Constitution_Verbatim]: This project is **greenfield** (`is_greenfield=true`). No constitution (`constitution_path=""`) exists yet. The `deviate-research` skill is expected to bootstrap a constitution from these exploration findings.

---

## [ARCHITECTURAL_BASELINES]

[Pattern_Over_Instance]: Only representative examples or base classes listed. All paths strictly relative to `repo_root`.

### Existing Architectural Patterns

- **LaTeX CV Template Architecture**: Root `.tex` files include content sections via `\input{}`. The `awesome-cv.cls` class file (vendored, 742 lines) defines all layout, styling, and commands. The project follows the Awesome-CV pattern from `https://github.com/posquit0/Awesome-CV`.

  ```
  \documentclass[11pt, a4paper]{awesome-cv}
  ...
  \input{cv/summary.tex}
  \input{cv/experience.tex}
  \input{cv/education.tex}
  \input{cv/projects.tex}
  \input{cv/skills.tex}
  \input{cv/ai_policy.tex}
  \input{cv/job_target.tex}
  ```

- **Bi-variant Resume Strategy**: Three root CV entry points, each including variant-specific sub-directories:
  - `W_Bisschoff_CV.tex` → includes `cv/*.tex` (standard/general)
  - `W_Bisschoff_CV_embedded.tex` → includes `cv/embedded/*.tex`
  - `W_Bisschoff_CV_enterprise.tex` → includes `cv/enterprise/*.tex`

- **Cover Letter Pattern**: Three cover letter entry points following the same variant pattern:
  - `W_Bisschoff_Cover_Letter.tex`
  - `W_Bisschoff_Cover_Letter_embedded.tex`
  - `W_Bisschoff_Cover_Letter_enterprise.tex`

- **Written Interview Document**: `written_interview.tex` (271 lines) — standalone LaTeX document for embedded software engineering interview responses.

### Infrastructure & Operations

- **CI/CD Pipeline** (`.github/workflows/release.yml`): Triggered on tag push (semver `v*` or calver `YYYY.MM*`). Uses `xu-cheng/latex-action@v3` with `xelatex` compiler. Compiles 3 CV PDF variants. Releases via `softprops/action-gh-release@v2`. No build-on-push or PR preview jobs exist.

  ```yaml
  on:
    push:
      tags:
        - "v*"
        - "[0-9][0-9][0-9][0-9].[0-9][0-9]*"
  permissions:
    contents: write
  ```

- **Docker Build** (`docker/Dockerfile` + `docker/build.sh`): Containerized LaTeX build using `texlive/texlive:latest`. The build script creates a Docker container, copies files in, runs `latexmk`, and copies output back.

- **Dev Container** (`.devcontainer/Dockerfile` + `.devcontainer/devcontainer.json` + `.devcontainer/postCreateCommand.sh`): VS Code dev container environment based on `texlive/texlive:latest`, adds `gh` CLI and Starship prompt.

- **VS Code Integration** (`.vscode/tasks.json`): Defines `build`, `continuous build`, and `full clean` tasks using `latexmk -pdfxe`.

- **No environment configuration files** (no `.env.example`, no secrets config, no deployment orchestration).

### Data & State Management

Not applicable. This is a static document generation repository with no database, caching, or async worker infrastructure.

### Quality, Safety & Observability

- **No test framework, no linting, no type checking** — the repo has zero quality automation.
- **No logging or metrics infrastructure**.
- **No auth/RBAC layer** (static PDFs only).
- The `.gitignore` excludes LaTeX auxiliary files (`*.aux`, `*.out`, `*.synctex.gz`, `build/`).

### External Integrations

- **Awesome-CV** (LaTeX class): Vendored from GitHub, used for all CV layout.
- **Roboto font family**: 10 TrueType font files vendored in `fonts/`.
- **FontAwesome**: 1 TrueType font file vendored in `fonts/`.
- **No API clients, webhooks, or third-party SDKs** present.

---

## [ECOSYSTEM_RESEARCH]

[Web_Discovery]: Findings from web search on Typst best practices for resume/CV, CI/CD, and ATS compatibility.

### Best Practices for ATS-Friendly Resume Layouts

- **Single-column layout** avoids ATS multi-column parsing issues. Source: `guillermodotn/clean-print-cv` (https://github.com/guillermodotn/clean-print-cv)
- **`ligatures: false`** on `set text()` prevents ATS character confusion. Source: `stuxf/basic-typst-resume-template` (https://github.com/stuxf/basic-typst-resume-template)
- **Standard section headings** (`Education`, `Experience`, `Skills`) improve ATS parsing. Source: multiple templates
- **YAML/JSON data separation** for content management is a common pattern. Source: `guillermodotn/clean-print-cv`
- **Clean PDF output** with standard reading order — no complex tables or color fills. Source: ecosystem consensus

  > ```typst
  > #set text(..., ligatures: false)
  > #set page(margin: (0.5in), ...)
  > ```

### CI/CD with GitHub Actions

Three distinct approaches exist in the ecosystem:

1. **`typst-community/setup-typst@v5`** — GitHub Action that installs the Typst binary and adds it to `PATH`. Most flexible, supports caching. Source: https://github.com/typst-community/setup-typst

  > ```yaml
  > - uses: typst-community/setup-typst@v5
  > - run: typst compile paper.typ paper.pdf
  > - uses: actions/upload-artifact@v6
  > ```

2. **`lvignoli/typst-action@main`** — Docker-based action. Source: https://github.com/lvignoli/typst-action

  > ```yaml
  > - name: Typst
  >   uses: lvignoli/typst-action@main
  >   with:
  >     source_file: main.typ
  > ```

3. **`ammar-ahmed22/compile-typst-action@v2`** — Supports multiple source paths and custom fonts. Source: https://github.com/ammar-ahmed22/compile-typst-action

### Bi-Variant Resume Pattern

Common ecosystem pattern: **data/presentation separation** using Typst imports.

- `guillermodotn/clean-print-cv`: YAML-driven, data in `cv-data.yaml`, layout in `cv-template.typ`
- `MrBogomips/mrbogo-cv`: Content in `content/`, template logic in `lib/`, entry point orchestrates imports
- `fruggiero/typst-jsonresume-cv`: JsonResume data files, layout in `base.typ`

  > ```
  > ├── cv.typ                  # Entry point - orchestrates imports
  > ├── content/                # YOUR DATA (edit these)
  > ├── lib/                    # TEMPLATE LOGIC (modify for layout changes)
  > ```

### Typst vs LaTeX for Resumes

Ecosystem consensus: Typst is a strong replacement for LaTeX for resume generation.

| Factor | Typst | LaTeX |
|--------|-------|-------|
| Compilation | Milliseconds | 1-30 seconds |
| Binary size | ~30 MB | ~4 GB (TeX Live) |
| Syntax | Markdown-like | TeX markup |
| ATS compatibility | Tie — both produce clean text PDFs | Established decades of support |
| Ecosystem maturity | Emerging | Established |

> "Migrating from LaTeX to Typst has been one of those very rare transitions where almost everything is better." — Mariano Zunino (https://mzunino.com.uy/til/2025/04/migrating-from-latex-to-typst/)

> "Compilations of the PDF were effectively instant. This is a far cry from LaTeX." — Sumner Evans (https://sumnerevans.com/posts/programming/learning-typst/)

---

## [FILE_REGISTRY]

| Path (Strictly Relative to Repo Root) | Type | Purpose | Verbatim Snippet (≤10 lines) |
| :--- | :--- | :--- | :--- |
| `W_Bisschoff_CV.tex` | Codebase_File | Main CV entry point — document preamble, personal info, and `\input` includes for 6 sections | `\documentclass[11pt, a4paper]{awesome-cv}` / `\input{cv/summary.tex}` / `\input{cv/experience.tex}` / `\input{cv/education.tex}` / `\input{cv/projects.tex}` / `\input{cv/skills.tex}` / `\input{cv/ai_policy.tex}` / `\input{cv/job_target.tex}` |
| `W_Bisschoff_CV_embedded.tex` | Codebase_File | Embedded-systems variant CV entry point — includes `cv/embedded/*` sections | `\position{Embedded Systems \& Real-Time Software Engineer}` / `\input{cv/embedded/summary.tex}` / `\input{cv/embedded/experience.tex}` / `\input{cv/embedded/education.tex}` / `\input{cv/embedded/projects.tex}` / `\input{cv/embedded/skills.tex}` |
| `W_Bisschoff_CV_enterprise.tex` | Codebase_File | Enterprise-systems variant CV entry point — includes `cv/enterprise/*` sections | `\position{Enterprise Systems \& Automation Architect}` / `\input{cv/enterprise/summary.tex}` / `\input{cv/enterprise/experience.tex}` / `\input{cv/enterprise/education.tex}` / `\input{cv/enterprise/projects.tex}` / `\input{cv/enterprise/skills.tex}` |
| `awesome-cv.cls` | Codebase_File | Vendored LaTeX class file (742 lines) from posquit0/Awesome-CV — defines all layout, colors, commands | `%% Start of file `awesome-cv.cls'.` / `% This class has been downloaded from:` / `% https://github.com/posquit0/Awesome-CV` |
| `cv/summary.tex` | Codebase_File | Professional summary section — single-paragraph profile | `\cvsection{Summary}` / `\begin{cvparagraph}` / `Software engineer with 5+ years of experience...` |
| `cv/experience.tex` | Codebase_File | Work experience section — 5 employers with bullet points (91 lines) | `\cvsection{Experience}` / `\cventry{Founder and Host}{Divergent Tabletop}{Cape Town}{Jul 2025 -- Present}` |
| `cv/education.tex` | Codebase_File | Education section — B.Eng. degree, project bullet points | `\cvsection{Education}` / `\cventry{B.Eng. Computer and Electronic Engineering}{North-West University}{Potchefstroom}{2020}` |
| `cv/projects.tex` | Codebase_File | Projects section — 2 projects (Wiki, FSM) with 2 more commented out | `\cvsection{Projects}` / `\cventry{Divergent Tabletop Wiki}{Community Knowledge Base}{Cape Town}{Jun 2025 -- Present}` |
| `cv/skills.tex` | Codebase_File | Skills matrix — 8 categories with sub-skills (65 lines) | `\cvsection{Skills}` / `\cvskill{Systems Architecture}{Event-driven FSM \skillsep RPC/IPC \skillsep State machines \skillsep Node trees}` |
| `cv/ai_policy.tex` | Codebase_File | AI Governance policy — SDD, Data Security, Engineering Rigour, Privacy by Design | `\cvsection{AI\ Governance \& Agentic Engineering}` / `I treat AI as an agentic partner within a strict engineering framework...` |
| `cv/job_target.tex` | Codebase_File | Job target statement — role preferences and constraints | `\cvsection{Job Target}` / `Seeking a mid to senior software engineering role (remote preferred, hybrid max. 2 days/week on-site in Cape Town)...` |
| `cv/opensource.tex` | Codebase_File | Open Source section (currently commented out from main CV) — 3 projects | `\cvsection{Open Source \& Side Projects}` / `\cventry{MeepleInn}{}{}{}{Phoenix/Elixir web application...}` |
| `cv/embedded/summary.tex` | Codebase_File | Embedded variant summary — positions as Systems Engineer | `Rigorous Systems Engineer with 5+ years of experience engineering real-time, event-driven software architectures (C/C++, FreeRTOS)...` |
| `cv/embedded/experience.tex` | Codebase_File | Embedded variant experience — emphasizes firmware/HIL/embedded roles | (71 lines, 5 employers, embedded-focused bullets) |
| `cv/embedded/education.tex` | Codebase_File | Embedded variant education — condensed bullet points | (16 lines) |
| `cv/embedded/skills.tex` | Codebase_File | Embedded variant skills — categorized as Primary/Secondary/Foundational/Other | (30 lines) |
| `cv/enterprise/summary.tex` | Codebase_File | Enterprise variant summary — positions as Enterprise Software Architect | `Strategic Enterprise Software Architect with 5+ years of experience engineering robust business automation platforms...` |
| `cv/enterprise/experience.tex` | Codebase_File | Enterprise variant experience — emphasizes ERP/Frappe/full-stack roles | (59 lines, 4 employers, enterprise-focused bullets) |
| `cv/enterprise/skills.tex` | Codebase_File | Enterprise variant skills — categorized as Primary/Secondary/Foundational/Other | (30 lines, Python/ERPNext/AWS focused) |
| `W_Bisschoff_Cover_Letter.tex` | Codebase_File | General cover letter — about-me and why-me sections (156 lines) | `% Awesome CV LaTeX Template for Cover Letter` / `% https://github.com/posquit0/Awesome-CV` |
| `W_Bisschoff_Cover_Letter_embedded.tex` | Codebase_File | Embedded-systems cover letter variant (125 lines) | (Cover letter tailored for embedded roles) |
| `W_Bisschoff_Cover_Letter_enterprise.tex` | Codebase_File | Enterprise cover letter variant (124 lines) | (Cover letter tailored for enterprise roles) |
| `written_interview.tex` | Codebase_File | Written interview response — embedded software engineering Q&A (271 lines) | `% Awesome CV LaTeX Template for Cover Letter` (uses Awesome-CV format for interview responses) |
| `analysis/experience_master.md` | Codebase_File | Canonical experience data source — master document for all employment history (98 lines) | `# Experience Master — Werner Bisschoff` / `This is the canonical source of truth for all employment experience.` |
| `analysis/wiki.md` | Codebase_File | Architectural analysis of Divergent Tabletop Wiki engine (112 lines) | Repository taxonomy, system design, interview artifacts for Elixir/BEAM wiki project |
| `analysis/wiki2.md` | Codebase_File | Second, more detailed architectural analysis (422 lines) | Deeper dive into Phoenix Wiki process topology, CRDT pipeline, STAR scenarios |
| `amazon-lp-cheatsheet-draft.md` | Codebase_File | Amazon Leadership Principles interview prep (538 lines) | `# Amazon LP Cheatsheet — Draft` / `## Leadership Principles: Story Index` |
| `.github/workflows/release.yml` | Config | GitHub Actions CI/CD — compiles 3 CV PDFs on tag push and publishes release | `name: Release CV` / `on: push: tags: - "v*" - "[0-9][0-9][0-9][0-9].[0-9][0-9]*"` |
| `docker/Dockerfile` | Config | Docker build image based on texlive/texlive:latest | `FROM texlive/texlive:latest` / `COPY *.cls ./` / `COPY fonts ./fonts/` / `RUN ["latexmk", "-pdfxe", "-quiet", "-output-directory=out", "-aux-directory=build"]` |
| `docker/build.sh` | Config | Shell wrapper for Docker-based LaTeX build | `docker build -t "$TAG" -f "docker/Dockerfile" .` / `docker cp "$(docker create "$TAG"):$OUTPUT_DIR" .` |
| `.devcontainer/devcontainer.json` | Config | VS Code Dev Container — TeX Live image + GitHub CLI mount | `"build": {"context": "..", "dockerfile": "../.devcontainer/Dockerfile"}` |
| `.devcontainer/Dockerfile` | Config | Dev container Dockerfile — TeX Live + gh CLI + Starship + user setup | `FROM texlive/texlive:latest` / `RUN apt-get update && apt-get install -y gh` / `RUN curl -sS https://starship.rs/install.sh \| sh -s -- --yes` |
| `.devcontainer/postCreateCommand.sh` | Config | Dev container post-create script | `sh <(curl -sS https://starship.rs/install.sh) --yes` / `apt-get update && apt-get install -y gh` |
| `.vscode/extensions.json` | Config | Recommended VS Code extensions | `{"recommendations": ["james-yu.latex-workshop"]}` |
| `.vscode/settings.json` | Config | VS Code LaTeX Workshop settings — Docker-based compilation recipes | `"latex-workshop.docker.enabled": true` / `"latex-workshop.docker.image.latex": "texlive/texlive"` |
| `.vscode/tasks.json` | Config | VS Code build/watch/clean tasks using latexmk | `"command": "latexmk -pdfxe -aux-directory=build *.tex"` |
| `fonts/` (directory, 11 files) | Asset | Vendored TrueType fonts: Roboto (10 weights) + FontAwesome | `Roboto-Regular.ttf`, `Roboto-Bold.ttf`, `FontAwesome.ttf`, etc. |
| `img/profile.jpg` | Asset | Profile photo for CV | (binary image — 1 file) |
| `img/profile2.jpg` | Asset | Alternate profile photo | (binary image — 1 file) |
| `example/education.tex` | Codebase_File | Awesome-CV template example — fictitious person, not Werner's data | `\cventry{B.S. in Computer Science and Engineering}{POSTECH(Pohang University of Science and Technology)}{Pohang, S.Korea}{Mar. 2010 - Aug. 2017}` |
| `example/experience.tex` | Codebase_File | Awesome-CV template example — fictitious work history | (Part of Awesome-CV template examples) |
| `example/summary.tex` | Codebase_File | Awesome-CV template example — fictitious summary | (Part of Awesome-CV template examples) |
| `example/committees.tex` | Codebase_File | Awesome-CV template example — committees section | (Part of Awesome-CV template examples) |
| `example/extracurricular.tex` | Codebase_File | Awesome-CV template example — extracurricular activities | (Part of Awesome-CV template examples) |
| `example/honors.tex` | Codebase_File | Awesome-CV template example — honors/awards | (Part of Awesome-CV template examples) |
| `example/presentation.tex` | Codebase_File | Awesome-CV template example — presentations | (Part of Awesome-CV template examples) |
| `example/writing.tex` | Codebase_File | Awesome-CV template example — writing samples | (Part of Awesome-CV template examples) |
| `.gitignore` | Config | Git exclusion rules — LaTeX aux, logs, editor files, OS files | `.git` / `build/` / `*.synctex.gz` / `*.aux` / `*.out` / `.DS_Store` |
| `.gitmodules` | Config | Empty file — no submodules configured | (0 bytes, empty) |

### Advisory / Non-CV Artifacts (Flagged for User Decision)

The following files are NOT part of the CV + CI + layout + cover letter core. User should decide whether to keep, migrate, or remove:

| Path | Type | Reason for Flag |
| :--- | :--- | :--- |
| `analysis/experience_master.md` | Analysis doc | Canonical experience data source — may be useful as migration reference, but not part of final CV output |
| `analysis/wiki.md` | Analysis doc | Architectural analysis of an external Elixir project (Divergent Tabletop Wiki) — unrelated to CV |
| `analysis/wiki2.md` | Analysis doc | Second, more detailed analysis of same external project — unrelated to CV |
| `amazon-lp-cheatsheet-draft.md` | Interview prep | Amazon Leadership Principles interview preparation — personal job-seeking material, not CV-related |
| `written_interview.pdf` | Binary (generated) | Output PDF from written_interview.tex |
| `written_interview.tex` | Codebase_File | Written interview response document — uses Awesome-CV template but is not a CV or cover letter |
| `img/profile.jpg` | Asset | Profile photo — may or may not be desired on Typst CV |
| `img/profile2.jpg` | Asset | Alternate profile photo |
| `example/` (8 files) | Codebase_File | Awesome-CV template example files — data for a fictitious person (Claud D. Park), not Werner's content |
| `*.pdf` (9 files) | Binary (generated) | Pre-compiled PDF outputs — should be regenerated by the new Typst CI, not committed |

---

## [STATUS_SUMMARY]

| Metric | Value |
| :--- | :--- |
| STATUS | SUCCESS |
| FEATURE_SLUG | 001-typst-cv-migration |
| GIT_BRANCH | main |
| SPEC_TARGET | specs/001-typst-cv-migration/explore.md |
| EPIC_ID | 001 |
| NEXT_ACTION | Run the `deviate-research` skill |
