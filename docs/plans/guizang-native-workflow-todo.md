# Guizang Native Workflow TODO

Date: 2026-06-03

## Goal

Turn Humanize PPT into a reliable upstream planner for Guizang, not a competing Guizang renderer.

## TODO 1: Make the Humanize -> Guizang Interface Explicit

- Define the Guizang production brief as Humanize's handoff artifact.
- Required outputs:
  - `research_dossier.md`
  - `ast_outline.md`
  - `deck_brief.md`
  - `slide_plan.json`
  - `guizang-production-prompt.md`
- The prompt must tell the next agent to use `guizang-ppt-skill/SKILL.md` and the correct Guizang template/layout/theme/checklist files.
- The prompt must distinguish Style A and Style B:
  - Style A: `assets/template.html`, `references/layouts.md`, `references/themes.md`
  - Style B: `assets/template-swiss.html`, `references/swiss-layout-lock.md`, `references/layouts-swiss.md`, `references/themes-swiss.md`

## TODO 2: Remove or Downgrade Misleading Renderer Adapter Behavior

- Audit scripts and docs for language that implies Humanize itself can produce 1:1 Guizang quality.
- Keep old adapter code only as a legacy/demo path if needed.
- Rename or document old adapter output as "template adapter" or "fallback preview", not "Guizang-native".
- Do not build a new renderer that copies Guizang template and injects custom sections.

## TODO 3: Add Native Guizang QA Requirements

- Use `examples/03-codex-guizang-native-ink-classic/index.html` as the current known-good Style A checkpoint.
- Style A QA must check:
  - no `[必填]`
  - no `SLIDES_HERE`
  - `canvas#bg-dark` exists
  - `canvas#bg-light` exists
  - `body.low-power` is not active by default
  - hero pages expose WebGL background
  - meaningful `data-anim` / `data-animate` markers exist
- Style B QA must run Guizang's `scripts/validate-swiss-deck.mjs`.
- Screenshot QA should save at least cover, one middle page, and closing page.

## Current Known-Good Evidence

- Deck path: `examples/03-codex-guizang-native-ink-classic/index.html`
- Preview screenshots:
  - `examples/03-codex-guizang-native-ink-classic/preview-slide-01.png`
  - `examples/03-codex-guizang-native-ink-classic/preview-slide-05.png`
  - `examples/03-codex-guizang-native-ink-classic/preview-slide-10.png`
- Verified behavior in the source experiment:
  - 10 slides
  - no template placeholders
  - 86 `data-anim` occurrences
  - WebGL context available
  - low-power mode off
  - screenshot pixel samples changed across time after hero transparency fix

## Non-Goals

- Do not push to GitHub in this checkpoint.
- Do not rewrite the whole Humanize runner in one pass.
- Do not remove existing examples.
- Do not modify the installed Guizang skill unless a separate task explicitly asks for it.

