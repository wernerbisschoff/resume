# AGENTS.md

### [PRESENTATION]

- Content in `content/data.typ`, layout in `lib/template.typ`
- Never mix data and layout logic
- No `.tex` or `.cls` files may be introduced

### [VERIFICATION]

- Always run `mise run check` before committing
- Verify new Typst source files compile: `typst compile <file>.typ`
- Check PDF output visually for layout shifts
- Install git hooks via `mise run hooks` (run after clone/setup)

### [GIT_HOOKS]

- Pre-commit runs `mise run check` for both Typst CV and Astro website
- Pre-push runs `mise run build` for both projects
- Install: `mise run hooks`
- Remove: `mise run uninstall-hooks`
- Bypass: `git commit --no-verify` or `git push --no-verify`

### [COMMIT]

- Scope: use `001` for Typst migration work (branch `feat/001-typst-cv-migration/*`)
- Convention: `type(scope): description`
