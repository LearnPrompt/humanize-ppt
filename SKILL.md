---
name: humanize-ppt
description: AST-based outline director and per-page media decision maker. Produces production briefs for native downstream PPT skills (guizang / frontend-slides / beautiful-html-templates) and runs a post-render QA loop on the rendered HTML. Use before generating PPT/HTML slides from raw material.
version: 0.6.5
author: LearnPrompt
license: MIT
requires-skills:
  guizang-ppt-skill: "Required when the deck language is Chinese. The brief writer references ~/.agents/skills/guizang-ppt-skill/SKILL.md; without it the next agent cannot render. v0.6.5 brief writer emits a stderr warning if the skill is not detected."
  frontend-slides: "Required when the deck language is English. Same hand-off pattern as guizang."
  beautiful-html-templates: "Optional English alternative. Same hand-off pattern."
metadata:
  tags: [presentation, ppt, html-slides, humanizer, ast, workflow, brief-orchestrator, hv-analysis, 9-styles]
---

# Humanize PPT

Use this skill when a user wants to turn raw material, notes, voice transcripts, documents, links, or old PPTs into a presentation-ready outline and per-page media decisions before delegating rendering to a downstream skill.

## Positioning

Humanize PPT is an **Outline Director**, **Per-Page Media Director**, **Production Brief Orchestrator**, and **Post-Render QA Loop Runner**, not a slide renderer.

It runs **before** downstream PPT / HTML slide skills and **around** the post-render QA loop. It owns the AST contract, the per-page media decision (does this page need a photo, a system diagram, a 10-second process clip, nothing?), the production brief that the next agent consumes, and the QA pass on the rendered HTML. It does **not** own the rendered HTML itself.

V0.6.4 is the **single entrypoint** for this loop. The user calls Humanize PPT once for the brief, hands the brief to a downstream skill for native rendering, then calls Humanize PPT again with `--qa-from <rendered.html>` to run a 3-iteration QA loop. Each iteration writes `qa_report.md` (findings), `fix_prompt.md` (downstream-skill-actionable corrections), and `qa_iteration.json` (round state). After 3 rounds with remaining findings, status flips to `needs-human`.

Humanize PPT never copies a downstream skill's template, never injects custom sections into it, and never post-processes the rendered HTML. When the downstream skill updates, Humanize PPT needs zero changes. This is the contract — see `references/guizang-production-brief-orchestrator.md` for the full brief specification.

For public positioning, describe Humanize PPT as a brief orchestrator that pairs with native downstream renderers. Do **not** frame it as a renderer itself, and do not present it as a "router" that picks the best visual style for the user — that decision lives in the brief, the downstream skill's own templates, and the human's review.

## AST theory

AST means **Audience-State-Transfer**.

- **Audience**: who is listening, what they know, what they resist, and why they would keep listening.
- **State**: the audience state before and after the deck, plus the core tension that blocks the transition.
- **Transfer**: the slide-by-slide path that moves the audience from initial state to desired state.

Core sentence:

> PPT is not an information container. PPT is an audience state-transfer artifact.

## Required output contract

For every Humanize PPT run, produce:

1. `deck_brief.md` — audience, goal, tension, success criteria.
2. `ast_outline.md` — AST map and narrative arc.
3. `slide_plan.json` — slide-by-slide plan, with per-page `media: {image, diagram, video}` decision and `layout_hint`.
4. `speaker_intent.md` — what the speaker should do on each slide. Downstream skills consume this as the source for their native speaker notes and presenter shell.
5. `asset_manifest.md` — Humanize's per-page material decisions: which page needs which kind of asset (image / diagram / video) and for what purpose.
6. `video_slots.json` — optional Remotion / HyperFrames / native video insertion plan.
7. `style_brief.md` — visual principle for downstream production.
8. `renderer_registry.json` — renderer capability snapshot for this run.
9. `router_plan.json` — selected primary renderer and staged route plan.
10. `commands/*.md` — bounded instructions for each downstream specialist agent.
11. `run_manifest.json` — final file inventory, route status, and QA status.
12. `<renderer>-production-prompt.md` — the production brief that the next agent consumes. v0.6.4 emits `guizang-production-prompt.md`, `frontend-slides-production-prompt.md`, or `beautiful-html-templates-production-prompt.md` depending on language and route. This file references the downstream skill's own `SKILL.md` and is the only thing the next agent needs to read.
13. `outputs/qa/qa_report.md` — first-pass QA gate (brief mode) or per-iteration QA findings (QA mode).

QA mode (post-render) additionally produces per iteration:

14. `outputs/qa/fix_prompt.md` — downstream-skill-actionable fix instructions.
15. `outputs/qa/qa_iteration.json` — round number, status (`iterate` / `pass` / `needs-human`), unresolved findings, history.

## Recommended OPC workflow (v0.6.4)

```text
O — Outline + Per-Page Media Direction
  Humanize PPT: raw material → AST outline + per-page media decision
  (deck_brief.md, ast_outline.md, slide_plan.json, speaker_intent.md,
   asset_manifest.md, video_slots.json, style_brief.md)

P — Native Renderer Invocation (100% downstream)
  zh  → guizang-ppt-skill        (Style A or B, native)
  en  → frontend-slides / beautiful-html-templates (native)
  Humanize emits the production prompt and stops. The downstream
  skill renders the deck. Humanize does NOT copy templates, does
  NOT inject SLIDES_HERE / [必填] replacements, does NOT add
  postMessage bridges to the rendered HTML.

Q — Conversational QA Loop on the rendered HTML
  Humanize --qa-from <rendered.html> reads the output of P, scans
  for failure modes (references/qa-failure-modes.md), writes
  qa_report.md and fix_prompt.md, tracks iteration in
  qa_iteration.json. Cap: 3 rounds. After cap with remaining
  findings, status flips to needs-human.

C — Complete / Control
  Downstream skill native speaker notes + presenter shell + deploy
  (Humanize does not own these in v0.6.4 — the brief tells the
  next agent to produce them in the downstream skill's own format)
```

## Rules

### v0.6.4 invariants (these are the hard rules; if you break any, you're off the v0.6.4 boundary)

1. **Humanize is brief-only.** It writes `<renderer>-production-prompt.md` and stops. It does **not** open, copy, or post-process the downstream skill's template. When the downstream skill updates its template, animation markers, or validator, Humanize needs zero changes.
2. **Downstream renderers are 100% native.** The next agent follows the downstream skill's own `SKILL.md`. The brief tells the next agent which skill to load, which Style (A/B) to use, which layouts to pick from, and which QA gates must pass — but it does not carry template internals.
3. **The QA loop caps at 3 iterations.** Round 4 with remaining fail findings is `needs-human`. The loop does not spin forever; it hands the decision back to a human.
4. **Speaker notes and presenter shell are downstream-skill-owned.** Humanize owns the semantic source (`speaker_intent.md`). The downstream skill produces the native speaker notes and presenter shell. Humanize does not inject `postMessage` bridges or `?slide=` URL parameters into the rendered HTML.
5. **The brief is the only thing the next agent reads.** It is a complete contract: deck metadata, per-page media decisions, style files, hard rules, known-good checkpoint, and per-style QA gates. The next agent does not need to re-derive intent from raw source material.

### Working rules

6. Do not let slide renderers consume raw material directly when Humanize PPT can first produce the AST contract.
7. Keep presenter mode as a downstream-skill completion step, not a Humanize style.
8. Absorb AI-writing cleanup principles from humanizer tools, but do not reduce Humanize PPT to text polishing.
9. Prefer a small verified workflow over a broad unverified promise.
10. For public Skill releases, create/push the repo, install from GitHub locally, run one safe full sample, verify the brief + QA loop on the verified known-good checkpoint (`examples/03-codex-guizang-native-ink-classic/`), and only then polish README details.
11. For Agent Teams development, emit `router_plan.json`, `run_manifest.json`, bounded `commands/*.md`, and the per-renderer production prompt before wiring real downstream Skills.
12. For WorkBuddy/CodeBuddy team upload packages, do **not** package demo or rendered HTML outputs as the team zip. The upload zip must mirror a team-plugin structure like `trading-team`: root-level `.codebuddy-plugin/plugin.json`, `agents/`, `skills/`, `rules/`, and `setting.json` (plus optional `avatars/`, `.workbuddy-plugin/`, `README.md`, `settings.json`). The `rules/` directory should include a scenario rule file such as `rules/<plugin-name>_rules.md` with frontmatter (`description`, `alwaysApply`, `enabled`, `updatedAt`, `provider`) and a `<system_reminder>` block describing available agents, skills, SOP, and usage requirements. Verify with `unzip -l` that the root is not `index.html/assets/screenshots/source` and is not folder-wrapped unless the target uploader explicitly requires a wrapper directory.
13. Do not treat HyperFrames/Remotion videos as a single embedded player that replaces PPT content. For Humanize PPT deliverables, video tools are **material producers**: transitions, explainer clips, before/after comparisons, talking-material inserts, social previews, and fallback stills that fill specific slide needs. The `media.video` decision per page (see `slide_plan.json` schema) tells the downstream skill which pages want a Remotion clip, for what purpose, and at what duration.

### Renderer-specific guidance (kept for history; the boundary itself is the invariants above)

14. For Chinese PPT production, the default stable path is `Humanize PPT → guizang-ppt-skill native → Humanize --qa-from → downstream presenter/deploy`. Guizang's own material QA and Swiss validator run inside the downstream skill. The `--qa-from` loop in Humanize is a second-pair-of-eyes pass, not a replacement.
15. For English PPT production, the default path is `Humanize PPT → frontend-slides or beautiful-html-templates (native) → Humanize --qa-from → downstream deploy`. The downstream skill owns its own template selection, preview gallery, and selected-template full deck. Humanize does not imitate them.
16. The verified Style A checkpoint at `examples/03-codex-guizang-native-ink-classic/` is a read-only visual reference. If the QA loop ever fails against it (`test_known_good_style_a_passes_all_style_a_gates`), the fixture or the live Guizang skill has drifted — do not weaken the QA check to make the test pass.

## Operational references

- `references/guizang-production-brief-orchestrator.md` — v0.6.4 canonical brief specification. The human + agent-facing contract for what `<renderer>-production-prompt.md` must contain and what it must not contain.
- `references/qa-failure-modes.md` — v0.6.4 failure mode catalog for the post-render QA loop. Human-readable; the code-side source of truth is `FAILURE_MODES` in `scripts/humanize_ppt_v2.py`.
- `references/agent-teams-public-preview.md` — Agent Teams architecture, specialist-agent command protocol, public preview release loop, and README split convention. (Historical; v0.6.4 collapses the Agent Teams model into a brief + QA loop.)
- `references/humanize-ppt-public-writing.md` — Public-facing positioning and article/script patterns: Humanize PPT as brief orchestrator, not a fixed 4-Skill bundle.
- `references/workbuddy-team-packaging-and-video-materials.md` — WorkBuddy/CodeBuddy team upload zip structure, validation script, scenario rules shape, and the Remotion/HyperFrames-as-material-producers pitfall.
- `references/guizang-material-qa.md` — Guizang downstream workflow, material production rules, Swiss visual QA checklist, and failure patterns learned from a full Humanize PPT → guizang deck pass. **Caveat:** these rules apply to the rendered HTML, not to the Humanize brief.
- `references/guizang-presenter-deploy.md` — Default Chinese PPT production path: guizang stable deck, material QA, presenter shell, and static deploy checks. **Caveat:** these rules apply to the rendered HTML, not to the Humanize brief.
- `references/beautiful-preview-first-adapter.md` — Durable adapter pattern for connecting `beautiful-html-templates`: version boundary, template selection, real title-slide previews, manifests, QA, and pitfalls. (Historical; v0.6.4 hands template selection to the downstream skill.)
- `references/selected-template-full-deck-adapter.md` — Durable adapter pattern for V0.4 selected-template full deck generation: required artifacts, routing, QA, and TDD coverage. (Historical.)
- `references/presenter-export-adapter.md` — Durable adapter pattern for adding V0.5-style presenter shell and export package after a final deck exists. (Historical; v0.6.4 hands presenter/export to the downstream skill.)
- `docs/versions/v0.6.4-guizang-production-brief-orchestrator.md` — v0.6.4 release notes: what changed, lessons, boundaries, known-good checkpoint, QA loop cap.
- `docs/versions/v0.2-router-edition.md` through `v0.6.3-english-style-gallery.md` — historical version notes, kept for context.
- `docs/versions/v0.4-selected-template-full-deck.md` — V0.4 Selected Template Full Deck notes: `--selected-template`, selected deck output, manifests, QA, and current boundaries.
- `docs/versions/v0.5-presenter-export-adapter.md` — V0.5 Presenter / Export Adapter notes: `--presenter-adapter`, `--export-adapter`, output artifacts, and boundaries.
- `docs/versions/v0.6.1-guizang-material-qa.md` — V0.6.1 Guizang material QA notes: downstream artifact recording, Remotion-as-material, SVG-safe Chinese diagrams, and visual review rules.
- `docs/versions/v0.6.2-guizang-presenter-deploy.md` — V0.6.2 Guizang presenter deploy notes: Chinese default path, `postMessage` presenter shell, and public static showcase.
- `docs/versions/v0.6.3-english-style-gallery.md` — V0.6.3 English style gallery notes: theme-first gate, five visible style candidates, and selected-style continuation.
- `docs/smoke-test.md` — No-dependency smoke check for validating the stable entrypoint on machines without pytest.
- `docs/plans/2026-05-25-release-readiness-checklist.md` — V0.6 release-readiness checklist and release-note draft.

## Quick start for agents (one-conversation flow)

v0.6.7 makes "install humanize-ppt + downstream skill + render" doable in **one agent session**. The brief itself contains the install commands the next agent needs:

```text
1. Verify humanize-ppt and downstream skill:
   test -f ~/.agents/skills/humanize-ppt/SKILL.md || echo "install humanize-ppt first"
   test -f ~/.agents/skills/guizang-ppt-skill/SKILL.md || { echo "missing guizang"; exit 1; }

2. Run Humanize PPT in brief mode:
   python3 ~/.agents/skills/humanize-ppt/scripts/humanize_ppt.py \
     --research-md <source.md> \
     --out <out> \
     --renderer guizang \
     --guizang-style A --guizang-theme ink-classic \
     --preview-outline    # human review checkpoint
   # review outline-preview.md, then:
   python3 ~/.agents/skills/humanize-ppt/scripts/humanize_ppt.py \
     --research-md <source.md> \
     --out <out> \
     --renderer guizang \
     --guizang-style A --guizang-theme ink-classic \
     --confirm-outline    # writes the production brief

3. Render via downstream skill, then QA:
   # (the brief contains step-by-step commands for the next agent;
   #  it includes the install command if guizang is missing)
   python3 ~/.agents/skills/humanize-ppt/scripts/humanize_ppt.py \
     --qa-from <rendered.html> \
     --out <out> \
     --renderer guizang \
     --guizang-style A \
     --max-qa-iterations 3
```

The brief itself contains a "Next agent's setup checklist" section with
5 explicit steps (verify, install-if-missing, re-verify, generate-media,
render). See `references/guizang-production-brief-orchestrator.md` for the
full contract.

## Local demo

The recommended stable entrypoint is `scripts/humanize_ppt.py`. Versioned scripts remain available for compatibility.

Brief mode (v0.6.4 default — writes a Guizang production brief, no HTML):

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --guizang-style A
```

The next agent reads `guizang-production-prompt.md` and renders natively via `guizang-ppt-skill`. Once the deck is rendered, run the post-render QA loop:

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update-v0.6.4/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

English paths use the same shape with `--renderer beautiful-html-templates` or `--renderer frontend-slides`, which write `beautiful-html-templates-production-prompt.md` or `frontend-slides-production-prompt.md` respectively.

The legacy V0.2-compatible entrypoint remains available for compatibility with earlier agents:

```bash
python3 scripts/humanize_ppt_v2.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.2 \
  --title "AI 工具更新，不只是功能清单" \
  --renderer auto
```

Legacy V0.1 demo remains available:

```bash
python3 scripts/humanize_ppt_v1.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单"
```
