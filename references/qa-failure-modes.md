# QA Failure Modes (v0.7.0)

Humanize PPT runs a **conversational QA loop** on rendered HTML before
signing off. This reference is the human-readable catalog of failure
modes the loop scans for. The code-side source of truth is the
`FAILURE_MODES` dict in `scripts/humanize_ppt_v2.py`; both stay in
sync by id.

**Catalog rule: only rules that actually exist in the code are listed.**
No aspirational modes, no invented checks. If a failure class is real
but not yet detected by the script, it is named in
[Not yet in the static scan](#not-yet-in-the-static-scan) — not dressed
up as a mode.

## Scope

Failure modes are grouped in two layers:

- **Layer 1 — renderer-agnostic failure classes.** The *symptom* can
  happen on any renderer's output. The *detection* currently
  implemented may still be renderer-specific (e.g. it matches guizang's
  placeholder markers); the class is generic, the rule is not.
- **Layer 2 — renderer-specific modes.** Scoped by renderer id:
  - **guizang** — both Style A and Style B unless noted
  - **guizang-style-a** — Style A only
  - **guizang-style-b** — Style B only (Swiss locked)
  - **frontend-slides** — reserved (see below)
  - **beautiful-html-templates** — reserved (see below)

## Layer 1 — renderer-agnostic failure classes

These are the failure *classes* the QA loop covers today, mapped to the
concrete rules that implement them. When English-renderer QA gets
verified, new rules land under the same classes.

| Failure class | What the audience sees | Implemented rules |
| --- | --- | --- |
| Template placeholder residue | Raw `[必填]` / `SLIDES_HERE`-style markers on a live slide | `placeholder-residue` |
| Animation degradation | Deck renders fully static; pacing collapses | `low-power-default`, `data-anim-thin` |
| Layout contract violation | Slide count / layout IDs in the HTML don't match `slide_plan.json` | `swiss-sxx-count-mismatch`, `swiss-sxx-invented-id`, `swiss-low-diversity` |
| Background layer missing | Hero/background visual layer absent, page looks unfinished | `webgl-canvas-missing` |
| AI draft residue | Model scaffolding ("作为AI", "首先我需要"…) visible on slides | brief-mode check `visible_slide_text_has_no_ai_draft_markers` (`BANNED_VISIBLE_PATTERNS` in `write_qa`) — runs on the slide plan in brief mode, before any render |

### Not yet in the static scan

Text overflow, low contrast, font-weight degradation, viewport
truncation, and image-text misalignment are real render failure classes
— but they need a real browser render to detect, and the static scan in
`scripts/humanize_ppt_v2.py` does **not** check them today. They are
deliberately *not* listed as modes (catalog rule above). Until Humanize
has a real detection, they live in the downstream visual checklists
(`references/guizang-material-qa.md`) and in human review.

## Mode catalog

Each mode gives: symptom → detection (the rule name in
`scripts/humanize_ppt_v2.py`) → fix-prompt direction (what
`fix_prompt.md` tells the downstream skill to do).

### `placeholder-residue` (guizang)

**Symptom:** template placeholders like `[必填]` or
`<!-- SLIDES_HERE -->` leaked into the rendered HTML. The downstream
skill did not finish its own substitution pass.

**Detection:** `check_placeholder_residue` — fail if `[必填]` or
`SLIDES_HERE` appears anywhere in the rendered HTML.

**Fix-prompt direction:** substitute all `[必填]` placeholders and
remove the `<!-- SLIDES_HERE -->` marker; the downstream skill's own
substitution pass must run end-to-end.

### `low-power-default` (guizang)

**Symptom:** `body.low-power` is active in the rendered HTML. This
suppresses animation and is meant to be a runtime opt-in, not a
default.

**Detection:** `check_low_power_default` — fail if the `<body>` class
list contains `low-power`.

**Fix-prompt direction:** remove `low-power` from the body class;
animation must play on first load.

### `webgl-canvas-missing` (guizang-style-a)

**Symptom:** the dual WebGL canvas (`canvas#bg-dark` and
`canvas#bg-light`) is absent or partially present. Without it the hero
background cannot render.

**Detection:** `check_webgl_canvas_missing` — fail unless both
`canvas#bg-dark` and `canvas#bg-light` exist in the rendered HTML.

**Fix-prompt direction:** add both canvases so the Style A WebGL hero
background can render.

### `data-anim-thin` (guizang-style-a)

**Symptom:** `data-anim` / `data-animate` markers are too few to drive
a watchable deck. The verified Ink Classic checkpoint has 86
occurrences.

**Detection:** `check_data_anim_thin` — hard failure below 3 markers,
soft warning below 10.

**Fix-prompt direction:** add more `data-anim` / `data-animate`
markers across non-cover pages; aim for 10+ (Ink Classic has 86).

### `swiss-sxx-count-mismatch` (guizang-style-b)

**Symptom:** the number of `data-layout="Sxx"` markers in the rendered
HTML does not equal the number of slides in `slide_plan.json`.

**Detection:** `check_swiss_sxx_count_mismatch` — fail if Sxx count ≠
slide count.

**Fix-prompt direction:** make the `data-layout="Sxx"` marker count
equal to the slide count in `slide_plan.json`; re-emit from the
downstream skill.

### `swiss-sxx-invented-id` (guizang-style-b)

**Symptom:** a `data-layout="Sxx"` value is not in the registered set
(`S01`–`S22`). The downstream skill invented a layout ID instead of
picking from the registered set in `references/layouts-swiss.md`.

**Detection:** `check_swiss_sxx_invented_id` — fail if any Sxx value ∉
S01..S22.

**Fix-prompt direction:** replace the invented Sxx values with
registered S01..S22 layout IDs.

### `swiss-low-diversity` (guizang-style-b, soft warning)

**Symptom:** fewer than 6 unique `Sxx` values across an 8-page deck
(or fewer than `ceil(slide_count * 0.6)` unique values for other
lengths). The deck reads as one layout stamped n times.

**Detection:** `check_swiss_low_diversity` — hard failure below 3
unique values, soft warning below the 60% floor.

**Fix-prompt direction:** diversify the Swiss layouts; pick a
different registered Sxx per slide where possible; floor is 60% unique
values.

## English renderers — reserved, and why

`frontend-slides` and `beautiful-html-templates` are marked
`"support_level": "brief-only"` in `registry/renderer_registry.json`:
the brief exit works (their production prompts are emitted and
consumable), but the `--qa-from` leg has **not** been verified on a
real rendered deck from either skill, and no renderer-specific rules
exist for them in `FAILURE_MODES`.

Their sections stay empty until a real frontend-slides /
beautiful-html-templates render goes through the QA loop and the
findings are verified. Empty over staged — same rule as the README
showcase.

## How the loop uses the catalog

1. `run_checks(html, plan, modes)` runs each mode's check function and
   returns a list of findings: `[{id, severity, pages, evidence}]`.
2. `_write_qa_report` emits the human-readable `qa_report.md`.
3. `_write_fix_prompt` emits a downstream-skill-actionable
   `fix_prompt.md` ("on S04 change `data-layout="S99"` to a registered
   Sxx layout, etc.").
4. Iteration tracker `qa_iteration.json` records the round number,
   which findings from the previous round were resolved, and which
   remain.

The loop caps at `--max-qa-iterations` (default 3). After the cap with
remaining findings, `qa_status` becomes `needs-human` and the next
agent or human takes over.
