<div align="center">

# Humanize PPT

## AST-based outline director for human-centered AI presentation workflows

**Turn raw material into an audience-aware production brief before rendering slides.**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[Live Preview](https://learnprompt.github.io/humanize-ppt/) · [中文](README.md) · [AST Theory](docs/AST-theory.md) · [OPC Workflow](docs/OPC-workflow.md) · [Agent Teams](docs/agent-teams.md)

</div>

---

## What is this?

Humanize PPT is an **outline director** for presentation workflows. It does not act as a template library. It first turns raw material into a production contract that is easier to present, render, QA, and adapt.

It uses AST theory:

- **Audience**: who is listening, what they know, and what they resist;
- **State**: where the audience starts and where the deck should move them;
- **Transfer**: how each slide moves the audience forward.

Core idea:

> PPT is not an information container. PPT is an audience state-transfer artifact.

## Quick start

New users only need one entrypoint:

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-preview \
  --title "AI 工具更新，不只是功能清单" \
  --style-mode preview-first
```

Open the result:

```bash
open .humanize-ppt-runs/ai-tool-update-preview/outputs/beautiful/previews/index.html
open .humanize-ppt-runs/ai-tool-update-preview/outputs/qa/qa_report.md
```

After selecting a Beautiful template, generate the full deck and optional presenter/export adapters:

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter
```

Legacy `scripts/humanize_ppt_v1.py` through `scripts/humanize_ppt_v5.py` remain available for compatibility and historical reproduction. README examples only recommend `scripts/humanize_ppt.py`.

## No-dependency smoke check

If pytest is unavailable, run the stdlib-only smoke check:

```bash
python3 scripts/smoke_check.py
```

It runs the stable entrypoint through a minimal path that does not require an external template library, then checks for:

```text
deck_brief.md
ast_outline.md
slide_plan.json
router_plan.json
run_manifest.json
outputs/qa/qa_report.md
```

See [docs/smoke-test.md](docs/smoke-test.md).

## Output shape

A run produces:

```text
out/
  deck_brief.md
  ast_outline.md
  slide_plan.json
  speaker_intent.md
  asset_manifest.md
  video_slots.json
  style_brief.md
  renderer_registry.json
  router_plan.json
  run_manifest.json
  commands/
    *.md
  outputs/
    beautiful/
    guizang/
    presenter/
    export/
    qa/
```

Some renderer-specific folders may be empty or marked pending depending on the selected route.

## Current boundaries

- Recommended entrypoint: `scripts/humanize_ppt.py`
- Compatibility entrypoints: `scripts/humanize_ppt_v1.py` through `scripts/humanize_ppt_v5.py`
- Historical version notes: `docs/versions/`
- Plans and reviews: `docs/plans/`
- Safe sample inputs: `examples/`

The current focus is a stable material → AST contract → preview/full deck → presenter/export → QA workflow. Broader renderer automation, video generation, deployment integrations, and team-package uploading are deferred.

## Live preview

- Home: https://learnprompt.github.io/humanize-ppt/
- Skill sharing deck showcase: https://learnprompt.github.io/humanize-ppt/showcase/skill-share/

Style exploration, presenter mode, and other generated demo modes are still being debugged, so their public entries are hidden for now.

## References

- [AST Theory](docs/AST-theory.md)
- [OPC Workflow](docs/OPC-workflow.md)
- [Agent Teams](docs/agent-teams.md)
- [Smoke Test](docs/smoke-test.md)
- [Version History](docs/versions/)
- [Release Readiness Checklist](docs/plans/2026-05-25-release-readiness-checklist.md)

## License

MIT
