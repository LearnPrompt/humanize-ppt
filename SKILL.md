---
name: humanize-ppt
description: A presentation system for agent-made PPTs — born for the talk, not just the template. It turns raw material into an AST (audience-state-transfer) outline where every page turn moves the audience forward, decides per-page visual enhancement (real images via baoyu-image-gen on the local Codex CLI, SVG diagrams, Remotion video), then runs a capped 3-round presentation checkup (演讲体检) on the rendered HTML, comparing each page against its outline page and writing fix prompts. The beautiful deck is rendered natively by a downstream template skill (broadly compatible with any HTML-PPT skill; verified: guizang-ppt-skill for Chinese, frontend-slides / beautiful-html-templates for English) — Humanize orchestrates the presentation, the template skill paints the slides. Use before generating PPT/HTML slides from raw material, and after rendering when the user says things like "帮我盯一下渲染出来的 PPT 有没有翻车", "PPT 渲染质检", "给这份 deck 做演讲体检", or "告诉我哪几页只能看不能讲". If all you want is one beautiful template page with no outline and no checkup, a rendering skill alone is enough; bring in Humanize when you need the talk's narrative before rendering and the checkup after.
version: 1.0.0
author: LearnPrompt
license: MIT
requires-skills:
  guizang-ppt-skill: "Required when the deck language is Chinese. The brief writer references ~/.agents/skills/guizang-ppt-skill/SKILL.md; without it the next agent cannot render. v0.6.5 brief writer emits a stderr warning if the skill is not detected."
  frontend-slides: "Recommended when the deck language is English. Same hand-off pattern as guizang. v1.0 support_level: full — brief exit works, full presentation checkup ran on a real deck on 2026-06-17 (docs/showcase/v0.9-frontend-slides/), and 5 renderer-specific failure-mode rules added (horizontal overflow, low contrast, hyphenation noise, font contract, image alt)."
  beautiful-html-templates: "English alternative. Same hand-off pattern. v1.0 support_level: full — brief exit works, full presentation checkup ran on a real Neo-Grid deck on 2026-06-13 (docs/showcase/hermes-agent-mastery/en/), same 5 renderer-specific failure-mode rules as frontend-slides."
  remotion-video-production: "Recommended (main) for the video media slot. Orchestrates the whole Remotion video pipeline — renders the real mp4 (deterministic loop, no narration) to the slot's asset_path. Verified in v0.9 (docs/showcase/v0.9-visual-enhancement/)."
  remotion-best-practices: "Pair with remotion-video-production while writing Remotion code — avoids unstable patterns (misused CSS / Tailwind animation, wrong asset paths)."
  remotion-video-toolkit: "Add only for complex video work — captions, charts, 3D, batch templates, automated render pipelines. Source: github.com/shreefentsar/remotion-video-toolkit."
  baoyu-image-gen: "Recommended for the image media slot. Drives the local Codex CLI (--provider codex-cli) using the logged-in Codex/ChatGPT subscription — no OPENAI_API_KEY needed. Generates the real hero/concept image to the slot's asset_path. Source: github.com/JimLiu/baoyu-skills. Verified in v0.9."
metadata:
  tags: [presentation, ppt, html-slides, humanizer, ast, workflow, brief-orchestrator, hv-analysis, 9-styles]
---

# Humanize PPT

Use this skill when a user wants to turn raw material, notes, voice transcripts, documents, links, or old PPTs into a presentation-ready outline and per-page media decisions before delegating rendering to a downstream skill.

## Positioning

Humanize PPT is a **presentation system, born for the talk**: an **Outline Director** (AST audience-state-transfer — every page turn moves the audience forward), a **Per-Page Visual-Enhancement Director** (real image / SVG diagram / Remotion video), a **Production Brief Orchestrator**, a **Presentation Checkup Runner** (演讲体检; formerly the QA loop, CLI flag still `--qa-from`), and a **Presenter-Mode hand-off**. The motivation: HTML-PPT template skills are great at *concept display* but blow a simple idea into a dozen pretty pages, while a real 90-minute talk is ~30 — the pretty shell outruns the content density. Humanize closes that gap: it keeps the beauty (rendered natively by the downstream template skill) and makes it *presentable* — a line you can stand up and deliver. Downstream template skills own "renders beautifully"; Humanize owns "it's a talk, and someone checked it."

The presentation checkup in one sentence: it does not grade beauty, it grades the outline. It compares every rendered page against its outline page, pulls out the pages that can only be looked at but not spoken from, and keeps going until every page is one the speaker can stand up and present. A failed page, in plain words: a page that holds only a few words and never finishes its point, or a page that fails the audience state transfer it promised (the listener walks out of that page in the same state they walked in). Such a page should not exist; the checkup pulls it out and generates fix instructions.

Humanize is broadly compatible with **any** downstream skill that can output an HTML PPT: the brief is plain markdown + JSON, anything can read it. The verified, stable recommendations are: Chinese → `guizang-ppt-skill`; English → `frontend-slides` / `beautiful-html-templates`. Other downstreams are hot-pluggable; support levels live in `registry/renderer_registry.json` and are updated only on real results.

It runs **before** downstream PPT / HTML slide skills and **around** the post-render presentation checkup. It owns the AST contract, the per-page media decision (does this page need a photo, a system diagram, a 10-second process clip, nothing?), the production brief that the next agent consumes, and the checkup pass on the rendered HTML. It does **not** own the rendered HTML itself.

There are two human review gates before rendering, both Humanize-owned zero-dependency working drafts (never decks): the **outline preview** (`--preview-outline` / `scripts/preview_outline_html.py`, the audience state-transfer map) and, since **v0.9**, the **style gallery** (`--style-gallery`). The style gallery is the cover-style gate: before the outline, Humanize emits ≥4 cover candidates for the renderer, writes one cover-only render command per candidate for the downstream skill to render, and stitches `style_gallery.html` to pick from. Humanize emits only the spec and the commands; the covers are rendered downstream. Picking a cover yields a re-injection command that carries the chosen style into the normal flow. See `references/style-gallery-spec.md`.

V0.6.4 is the **single entrypoint** for this loop. The user calls Humanize PPT once for the brief, hands the brief to a downstream skill for native rendering, then calls Humanize PPT again with `--qa-from <rendered.html>` to run the 3-iteration presentation checkup. Each iteration writes `qa_report.md` (findings), `fix_prompt.md` (downstream-skill-actionable corrections), and `qa_iteration.json` (round state). After 3 rounds with remaining findings, status flips to `needs-human`.

Humanize PPT never copies a downstream skill's template, never injects custom sections into it, and never post-processes the rendered HTML. When the downstream skill updates, Humanize PPT needs zero changes. This is the contract — see `references/guizang-production-brief-orchestrator.md` for the full brief specification.

For public positioning, describe Humanize PPT as a brief orchestrator that pairs with native downstream renderers. Do **not** frame it as a renderer itself, and do not present it as a "router" that picks the best visual style for the user — that decision lives in the brief, the downstream skill's own templates, and the human's review. When a user only wants a pretty template page, that is a rendering-skill job, not a Humanize job: state the choice, not a prohibition.

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

Style-gallery mode (`--style-gallery`, pre-outline gate) instead produces and stops:

16. `style_gallery.html` — zero-dependency picker stitching ≥4 candidate covers.
17. `style_gallery_plan.json` — per-candidate id, cli, command_file, cover paths, re-injection command.
18. `commands/style-gallery/<id>.md` — one cover-only render command per candidate (downstream renders only S01 → `outputs/style-gallery/<id>/cover.{html,png}`).

## Recommended OPC workflow (v0.6.4)

```text
O — Outline + Per-Page Media Direction
  Humanize PPT: raw material → AST outline + per-page media decision
  (deck_brief.md, ast_outline.md, slide_plan.json, speaker_intent.md,
   asset_manifest.md, video_slots.json, style_brief.md)

P — Native Renderer Invocation (100% downstream)
  zh  → guizang-ppt-skill        (Style A or B, native; recommended)
  en  → frontend-slides / beautiful-html-templates (native; recommended)
  other HTML-PPT skills → hot-pluggable, same brief contract
  Humanize emits the production prompt and stops. The downstream
  skill renders the deck. Humanize does NOT copy templates, does
  NOT inject SLIDES_HERE / [必填] replacements, does NOT add
  postMessage bridges to the rendered HTML.

Q — Presentation Checkup (演讲体检) on the rendered HTML
  Humanize --qa-from <rendered.html> reads the output of P,
  compares pages against the outline, scans for failure modes
  (references/qa-failure-modes.md), writes qa_report.md and
  fix_prompt.md, tracks iteration in qa_iteration.json.
  Cap: 3 rounds. After cap with remaining findings, status
  flips to needs-human.

C — Complete / Control
  Downstream skill native speaker notes + presenter shell + deploy
  (Humanize does not own these in v0.6.4 — the brief tells the
  next agent to produce them in the downstream skill's own format)
```

## Rules

### v0.6.4 invariants (these are the hard rules; if you break any, you're off the v0.6.4 boundary)

1. **Humanize is brief-only.** It writes `<renderer>-production-prompt.md` and stops. It does **not** open, copy, or post-process the downstream skill's template. When the downstream skill updates its template, animation markers, or validator, Humanize needs zero changes.
2. **Downstream renderers are 100% native.** The next agent follows the downstream skill's own `SKILL.md`. The brief tells the next agent which skill to load, which Style (A/B) to use, which layouts to pick from, and which QA gates must pass — but it does not carry template internals.
3. **The presentation checkup caps at 3 iterations.** Round 4 with remaining fail findings is `needs-human`. The loop does not spin forever; it hands the decision back to a human.
4. **Speaker notes and presenter shell — Humanize produces a baseline `presenter-shell.html`; downstream owns the full stage.** Humanize owns the semantic source (`speaker_intent.md`) and now also writes `outputs/presenter/presenter-shell.html` directly from `slide_plan.json` + `speaker_intent.md` (usable standalone, even before the downstream deck exists). The downstream skill produces the native speaker notes and fuller presenter console. Humanize does not inject `postMessage` bridges or `?slide=` URL parameters into the rendered HTML.
5. **The brief is the only thing the next agent reads.** It is a complete contract: deck metadata, per-page media decisions, style files, hard rules, known-good checkpoint, and per-style QA gates. The next agent does not need to re-derive intent from raw source material.

### Working rules

6. Do not let slide renderers consume raw material directly when Humanize PPT can first produce the AST contract.
7. Keep the downstream skill as the owner of the full stage view; Humanize's `presenter-shell.html` is a functional baseline, not a replacement for native consoles.
8. Absorb AI-writing cleanup principles from humanizer tools, but do not reduce Humanize PPT to text polishing.
9. Prefer a small verified workflow over a broad unverified promise.
10. For public Skill releases, create/push the repo, install from GitHub locally, run one safe full sample, verify the brief + presentation checkup on the verified known-good checkpoint (`examples/03-codex-guizang-native-ink-classic/`), and only then polish README details.
11. For Agent Teams development, emit `router_plan.json`, `run_manifest.json`, bounded `commands/*.md`, and the per-renderer production prompt before wiring real downstream Skills.
12. For WorkBuddy/CodeBuddy team upload packages, do **not** package demo or rendered HTML outputs as the team zip. The upload zip must mirror a team-plugin structure like `trading-team`: root-level `.codebuddy-plugin/plugin.json`, `agents/`, `skills/`, `rules/`, and `setting.json` (plus optional `avatars/`, `.workbuddy-plugin/`, `README.md`, `settings.json`). The `rules/` directory should include a scenario rule file such as `rules/<plugin-name>_rules.md` with frontmatter (`description`, `alwaysApply`, `enabled`, `updatedAt`, `provider`) and a `<system_reminder>` block describing available agents, skills, SOP, and usage requirements. Verify with `unzip -l` that the root is not `index.html/assets/screenshots/source` and is not folder-wrapped unless the target uploader explicitly requires a wrapper directory.
13. Do not treat HyperFrames/Remotion videos as a single embedded player that replaces PPT content. For Humanize PPT deliverables, video tools are **material producers**: transitions, explainer clips, before/after comparisons, talking-material inserts, social previews, and fallback stills that fill specific slide needs. The `media.video` decision per page (see `slide_plan.json` schema) tells the downstream skill which pages want a Remotion clip, for what purpose, and at what duration.

### Renderer-specific guidance (kept for history; the boundary itself is the invariants above)

14. For Chinese PPT production, the recommended stable path is `Humanize PPT → guizang-ppt-skill native → Humanize --qa-from → downstream presenter/deploy`. Guizang's own material QA and Swiss validator run inside the downstream skill. The presentation checkup in Humanize is a second-pair-of-eyes pass, not a replacement.
15. For English PPT production, the recommended path is `Humanize PPT → frontend-slides or beautiful-html-templates (native) → Humanize --qa-from → downstream deploy`. The downstream skill owns its own template selection, preview gallery, and selected-template full deck. Humanize does not imitate them. **v1.0 support levels** (see `registry/renderer_registry.json`): both `beautiful-html-templates` and `frontend-slides` are now `full` — brief exit works, full presentation checkup ran on real decks, and 5 renderer-specific failure-mode rules added (horizontal overflow, low contrast, hyphenation noise, font contract, image alt). Screenshot review is still part of the checkup methodology for cases the static scan can't reach.
16. The verified Style A checkpoint at `examples/03-codex-guizang-native-ink-classic/` is a read-only visual reference. If the presentation checkup ever fails against it (`test_known_good_style_a_passes_all_style_a_gates`), the fixture or the live Guizang skill has drifted — do not weaken the checkup to make the test pass. The same applies to the English checked-up deck at `docs/showcase/hermes-agent-mastery/en/ppt/` (`test_english_showcase_deck_passes_presentation_checkup`).

## Operational references

- `references/guizang-production-brief-orchestrator.md` — v0.6.4 canonical brief specification. The human + agent-facing contract for what `<renderer>-production-prompt.md` must contain and what it must not contain.
- `SPEC.md` — engine technical specification: boundary, CLI surface (mode-check order), data flow, output contract, the v0.9 style gallery, the presentation checkup, the per-page media model, and the renderer registry. The authoritative "what the engine does and guarantees" reference.
- `references/qa-failure-modes.md` (+ English mirror `references/qa-failure-modes.en.md`) — failure mode catalog for the presentation checkup (演讲体检): a renderer-agnostic failure-class layer plus guizang-specific modes, each with what the audience would see. Human-readable; the code-side source of truth is `FAILURE_MODES` in `scripts/humanize_ppt_v2.py`. Includes the WebGL-hero static-screenshot capture trap as a "static scan can't catch yet" class.
- `references/style-gallery-spec.md` — v0.9 spec for the `--style-gallery` cover-style gate: candidates, cover-only commands, the zero-dependency picker, re-injection, and the WebGL screenshot warning.
- `scripts/preview_outline_html.py` — outline preview: renders the audience state-transfer map (one zero-dependency single-file HTML; per-slide enter-state → intent → leave-state rows plus a state-arc summary) from `slide_plan.json`. Real sample: `examples/04-preview-outline-ai-tool-update/`.
- `scripts/record_demo_gif.py` — records the style gallery + outline preview (the two zero-dependency working drafts) into one demo GIF (requires playwright + ffmpeg). The gallery covers are downstream-rendered; `--covers-dir` overlays real covers before recording.
- `docs/versions/v0.9.0-style-gallery.md` — v0.9 release notes: the cover-style gallery gate, the WebGL static-screenshot failure class, the English failure-mode mirror, SPEC.md, and the README/GIF-slot work.
- `docs/versions/v0.8.0-presentation-checkup.md` — v0.8.0 release notes: why the QA loop was renamed to presentation checkup, the hot-pluggable route framing, the plain-language usage rewrite, and the verified English checkup run.
- `docs/versions/v0.7.0-render-qa-inspector.md` — v0.7.0 release notes: why the positioning moved to render-QA inspector, English-path support levels, and the outline preview artifact.
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

The next agent reads `guizang-production-prompt.md` and renders natively via `guizang-ppt-skill`. Once the deck is rendered, run the presentation checkup:

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update-v0.6.4/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

English paths use the same shape with `--renderer beautiful-html-templates` or `--renderer frontend-slides`, which write `beautiful-html-templates-production-prompt.md` or `frontend-slides-production-prompt.md` respectively. (v0.9: both `beautiful-html-templates` and `frontend-slides` are `support_level: brief+qa-verified` — beautiful after the 2026-06-13 real-deck checkup, frontend-slides after a real-deck checkup on 2026-06-17. The v0.9 style-gallery gate itself changed no support level — those move only on real rendered output.)

Outline preview (audience state-transfer map from an existing `slide_plan.json`, zero-dependency single-file HTML):

```bash
python3 scripts/preview_outline_html.py \
  --slide-plan .humanize-ppt-runs/ai-tool-update-v0.6.4/slide_plan.json \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4/preview-outline.html \
  --title "AI 工具更新，不只是功能清单"
```

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
