# QA Failure Modes (v0.6.4)

Humanize PPT runs a **conversational QA loop** on rendered HTML before
signing off. This reference is the human-readable catalog of failure
modes the loop scans for. The code-side source of truth is the
`FAILURE_MODES` dict in `scripts/humanize_ppt_v2.py`; both stay in
sync by id.

## Scope

Failure modes are grouped by which renderer they apply to:

- **guizang** — both Style A and Style B unless noted
- **guizang-style-a** — Style A only
- **guizang-style-b** — Style B only (Swiss locked)
- **frontend-slides** — reserved for future
- **beautiful-html-templates** — reserved for future

## Mode catalog

### `placeholder-residue` (guizang)

Template placeholders like `[必填]` or `<!-- SLIDES_HERE -->` leaked
into the rendered HTML. Means the downstream skill did not finish its
own substitution pass.

**Pass condition:** no `[必填]` and no `SLIDES_HERE` in the rendered HTML.

### `low-power-default` (guizang)

`body.low-power` is active in the rendered HTML. This suppresses
animation and is meant to be a runtime opt-in, not a default.

**Pass condition:** body tag does not include the `low-power` class.

### `webgl-canvas-missing` (guizang-style-a)

The dual WebGL canvas (`canvas#bg-dark` and `canvas#bg-light`) is
absent or partially present. Without it the hero background cannot
render.

**Pass condition:** both `canvas#bg-dark` and `canvas#bg-light` exist
in the rendered HTML.

### `data-anim-thin` (guizang-style-a)

`data-anim` / `data-animate` markers are too few to drive a watchable
deck. The verified Ink Classic checkpoint has 86 occurrences.

**Pass condition:** at least 3 `data-anim` markers total (Ink Classic
floor). Below 10 is a soft warning; below 3 is a hard failure.

### `swiss-sxx-count-mismatch` (guizang-style-b)

The number of `data-layout="Sxx"` markers in the rendered HTML does
not equal the number of slides in `slide_plan.json`.

**Pass condition:** Sxx count == slide count.

### `swiss-sxx-invented-id` (guizang-style-b)

A `data-layout="Sxx"` value is not in the registered set
(`S01`-`S22`). Means the downstream skill invented a layout ID
instead of picking from the registered set in
`references/layouts-swiss.md`.

**Pass condition:** every Sxx value ∈ S01..S22.

### `swiss-low-diversity` (guizang-style-b, soft warning)

Fewer than 6 unique `Sxx` values across an 8-page deck (or fewer
than `ceil(slide_count * 0.6)` unique values for other lengths).
Hard failure below 3 unique values.

**Pass condition:** unique Sxx count ≥ 3 and ≥ 60% of slide count.

## How the loop uses the catalog

1. `run_checks(html, plan, modes)` runs each mode's check function and
   returns a list of findings: `[{id, severity, pages, evidence}]`.
2. `write_qa_report` emits the human-readable `qa_report.md`.
3. `write_fix_prompt` emits a downstream-skill-actionable
   `fix_prompt.md` ("on S04 change `data-layout="S99"` to a registered
   Sxx layout, etc.").
4. Iteration tracker `qa_iteration.json` records the round number,
   which findings from the previous round were resolved, and which
   remain.

The loop caps at `--max-qa-iterations` (default 3). After the cap with
remaining findings, `qa_status` becomes `needs-human` and the next
agent or human takes over.
