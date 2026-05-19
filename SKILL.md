---
name: humanize-ppt
description: AST-based outline director and router for human-centered AI presentation workflows. Use before generating PPT/HTML slides from raw material, or as the single entrypoint that routes to downstream PPT Skills.
version: 0.5.0
author: LearnPrompt
license: MIT
metadata:
  tags: [presentation, ppt, html-slides, humanizer, ast, workflow]
---

# Humanize PPT

Use this skill when a user wants to turn raw material, notes, voice transcripts, documents, links, or old PPTs into a presentation-ready outline before rendering slides.

## Positioning

Humanize PPT is an **Outline Director**, **Renderer Router**, and **Agent Teams Orchestrator**, not a fixed slide renderer.

It should run before downstream PPT / HTML slide skills. Its job is to produce a clean AST-based production brief so renderers do not ingest raw noisy material directly.

V0.5 can also be used as the **single entrypoint**: the user calls Humanize PPT once, Humanize PPT writes the AST contract, chooses a renderer route, emits bounded `commands/*.md` for downstream agents, records `router_plan.json` / `run_manifest.json`, runs a first QA gate, can render a real `beautiful-html-templates` preview-first gallery, can use `--selected-template <slug>` to turn one selected Beautiful template into a full deck, and can add `--presenter-adapter` / `--export-adapter` to generate a presenter shell and portable export package. This does not mean Humanize PPT owns every visual template; it owns the decision, completion adapters, and production contract.

For public positioning and propagation, describe Humanize PPT as a contract/orchestration layer that can adapt to many different outline-producing Skills. Do **not** frame it as being limited to a fixed list of four Skills. It is fine to recommend specific HTML PPT Skills as good downstream renderers, but present them as suggested pairings, not as the product boundary.

In Agent Teams mode, the main Humanize PPT Agent loads this skill and controls specialist agents:

- Guizang Agent for Chinese stable rendering.
- Zara Agent for style exploration, HTML production, and deploy.
- HyperFrames Agent for video slots.
- Presenter Agent for presenter mode after the deck is finalized.
- QA Agent for content, visual, path, and delivery checks.

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
3. `slide_plan.json` — slide-by-slide plan.
4. `speaker_intent.md` — what the speaker should do on each slide.
5. `asset_manifest.md` — screenshots, charts, images, video needs.
6. `video_slots.json` — optional HyperFrames / video insertion plan.

V0.5 router runs also produce:

7. `renderer_registry.json` — renderer capability snapshot for this run.
8. `style_brief.md` — visual/routing principle for downstream production.
9. `router_plan.json` — selected primary renderer and staged route plan.
10. `commands/*.md` — bounded instructions for each downstream specialist agent.
11. `run_manifest.json` — final file inventory, route status, and QA status.
12. `outputs/qa/qa_report.md` — first-pass quality gate.
13. `outputs/beautiful/previews/index.html` — when preview-first routes to `beautiful-html-templates`, a real 3-template title-slide gallery.
14. `outputs/beautiful/preview_manifest.json` — selected templates, scores, reasons, and preview paths.
15. `outputs/beautiful/selected/index.html` — when `--selected-template <slug>` is provided, the selected Beautiful template rendered as a full deck.
16. `outputs/beautiful/selected_manifest.json` — selected template slug, deck path, and slide count.
17. `outputs/presenter/index.html` / `presenter_manifest.json` — when `--presenter-adapter` is provided after a final deck exists.
18. `outputs/export/package/`, `export_pdf.sh`, `export_manifest.json` — when `--export-adapter` is provided after a final deck exists.

## Recommended OPC workflow

```text
O — Outline Director
  Humanize PPT: raw material → AST outline + production brief

P — Presentation Production
  guizang path: Chinese stable HTML PPT
  beautiful-html-templates path: 3-template preview-first style exploration + selected-template full deck
  html-ppt path: full deck templates + presenter mode
  frontend-slides path: PPTX conversion + style discovery

C — Complete / Control
  HyperFrames video adapter
  Presenter Adapter shell
  Deploy / export adapter
  QA checklist
```

## Rules

1. Do not let slide renderers consume raw material directly when Humanize PPT can first produce the AST contract.
2. Keep presenter mode as a post-processing adapter, not a style.
3. Separate deployment from presenter mode.
4. Absorb AI-writing cleanup principles from humanizer tools, but do not reduce Humanize PPT to text polishing.
5. Prefer a small verified workflow over a broad unverified promise.
6. For public Skill releases, create/push the repo, install from GitHub locally, run one safe full sample, verify style exploration + presenter mode + deploy URL, and only then polish README details.
7. For Agent Teams development, emit `router_plan.json`, `run_manifest.json`, bounded `commands/*.md`, and separate `outputs/<agent>/` directories before wiring real downstream Skills.
8. For WorkBuddy/CodeBuddy team upload packages, do **not** package demo or rendered HTML outputs as the team zip. The upload zip must mirror a team-plugin structure like `trading-team`: root-level `.codebuddy-plugin/plugin.json`, `agents/`, `skills/`, `rules/`, and `setting.json` (plus optional `avatars/`, `.workbuddy-plugin/`, `README.md`, `settings.json`). The `rules/` directory should include a scenario rule file such as `rules/<plugin-name>_rules.md` with frontmatter (`description`, `alwaysApply`, `enabled`, `updatedAt`, `provider`) and a `<system_reminder>` block describing available agents, skills, SOP, and usage requirements. Verify with `unzip -l` that the root is not `index.html/assets/screenshots/source` and is not folder-wrapped unless the target uploader explicitly requires a wrapper directory.
9. Do not treat HyperFrames/Remotion videos as a single embedded player that replaces PPT content. For Humanize PPT deliverables, video tools are **material producers**: transitions, explainer clips, before/after comparisons, talking-material inserts, social previews, and fallback stills that fill specific slide needs. If a PPT page feels empty, first decide whether it needs an explanatory image, flow diagram, before/after visual, screenshot evidence, transition fragment, or short narration clip; only then route to GPT image / HyperFrames / Remotion.
10. When `beautiful-html-templates` is the preview-first route, do not stop at a planned command file. A connected path must produce real `outputs/beautiful/previews/index.html`, three candidate title-slide previews, `preview_manifest.json`, a render report, and a QA-visible route status. Treat this as V0.3+ capability, because it changes the user-facing workflow from routing advice to visible style selection.
11. When the user chooses a Beautiful candidate, run V0.4+ `--selected-template <slug>` and produce a real full deck at `outputs/beautiful/selected/index.html` plus `selected_manifest.json`. Do not call this complete if only the preview gallery exists.
12. In V0.5, presenter/export are post-processing adapters. They require a rendered final deck (`outputs/<renderer>/index.html` or `outputs/beautiful/selected/index.html`), not just a preview gallery.

## Operational references

- `references/agent-teams-public-preview.md` — Agent Teams architecture, specialist-agent command protocol, public preview release loop, and README split convention.
- `references/humanize-ppt-public-writing.md` — Public-facing positioning and article/script patterns: Humanize PPT as adaptable outline/director layer, not a fixed 4-Skill bundle.
- `references/workbuddy-team-packaging-and-video-materials.md` — WorkBuddy/CodeBuddy team upload zip structure, validation script, scenario rules shape, and the Remotion/HyperFrames-as-material-producers pitfall.
- `references/beautiful-preview-first-adapter.md` — Durable adapter pattern for connecting `beautiful-html-templates`: version boundary, template selection, real title-slide previews, manifests, QA, and pitfalls.
- `references/selected-template-full-deck-adapter.md` — Durable adapter pattern for V0.4 selected-template full deck generation: required artifacts, routing, QA, and TDD coverage.
- `references/presenter-export-adapter.md` — Durable adapter pattern for adding V0.5-style presenter shell and export package after a final deck exists.
- `docs/v0.2-router-edition.md` — V0.2 Router Edition notes kept for history.
- `docs/v0.3-preview-first.md` — V0.3 Preview-First implementation notes: real `beautiful-html-templates` preview gallery, template selection, manifests, and version boundary.
- `docs/v0.4-selected-template-full-deck.md` — V0.4 Selected Template Full Deck notes: `--selected-template`, selected deck output, manifests, QA, and current boundaries.
- `docs/v0.5-presenter-export-adapter.md` — V0.5 Presenter / Export Adapter notes: `--presenter-adapter`, `--export-adapter`, output artifacts, and boundaries.

## Local demo

If this repository is installed locally, run V0.5 Presenter / Export Adapter:

```bash
python3 scripts/humanize_ppt_v5.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.5-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter
```

Preview-first routing still renders real Beautiful previews:

```bash
python3 scripts/humanize_ppt_v3.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.3-preview \
  --title "AI 工具更新，不只是功能清单" \
  --style-mode preview-first
```

The legacy V0.2-compatible entrypoint remains available:

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
