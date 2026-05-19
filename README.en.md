<div align="center">

# Humanize PPT

## AST-based outline director for human-centered AI presentation workflows

**Turn raw material into an audience-aware deck brief before rendering slides.**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[Live Preview](https://learnprompt.github.io/humanize-ppt/) · [中文](README.md) · [AST Theory](docs/AST-theory.md) · [OPC Workflow](docs/OPC-workflow.md) · [Agent Teams](docs/agent-teams.md)

</div>

---

## What is this?

Humanize PPT is an **outline director** for presentation workflows. It is not another slide template and not a normal text humanizer.

It uses AST theory to turn raw material into a structured production brief:

- who the audience is;
- what state they are in before the deck;
- what state they should reach after the deck;
- what the core cognitive tension is;
- how each slide moves the audience forward;
- which downstream renderer or adapter should finish the job.

The clean brief can then be passed to downstream tools such as guizang, Zara-style HTML deck exploration, HyperFrames, presenter shells, or deployment adapters.

## Core idea

> **PPT is not an information container. PPT is an audience state-transfer artifact.**

When AI generates slides directly from raw material, the problem is often not visual quality. The bigger problem is that reasoning traces, explanatory noise, summary voice, and bloated structure leak into the deck.

Humanize PPT cleans and reorganizes the material into a presentation path before slide rendering starts.

## V0.5 public preview

V0.5 validates a complete deck loop:

```text
Raw material
→ Humanize PPT / AST Outline Director
→ Style exploration HTML deck
→ Selected-template full deck
→ Presenter Adapter shell
→ Export Adapter package
```

It includes:

- `SKILL.md` — agent skill entrypoint;
- `docs/AST-theory.md` — AST theory;
- `docs/OPC-workflow.md` — Outline / Produce / Complete workflow;
- `contracts/` — output contract templates;
- `scripts/humanize_ppt_v5.py` — Presenter / Export Adapter entrypoint;
- `scripts/humanize_ppt_v4.py` — Selected Template Full Deck wrapper;
- `scripts/humanize_ppt_v1.py` — deterministic legacy demo runner;
- `examples/` — safe sample inputs.

## Quick start

```bash
git clone https://github.com/LearnPrompt/humanize-ppt.git
cd humanize-ppt

python3 scripts/humanize_ppt_v5.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.5-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter

open .humanize-ppt-runs/ai-tool-update-v0.5-complete/outputs/beautiful/selected/index.html
open .humanize-ppt-runs/ai-tool-update-v0.5-complete/outputs/presenter/index.html
open .humanize-ppt-runs/ai-tool-update-v0.5-complete/outputs/export/package/index.html
```

Run the Hermes installation explainer demo:

```bash
python3 scripts/humanize_ppt_v1.py   --source examples/02-hermes-install-guide/source.md   --out .humanize-ppt-runs/hermes-install   --title "把 Hermes 装成一个真正能干活的 Agent"
```

## Live preview

- Home: https://learnprompt.github.io/humanize-ppt/
- Skill sharing deck showcase: https://learnprompt.github.io/humanize-ppt/showcase/skill-share/

Style exploration, presenter mode, and other generated demo modes are still being debugged, so their public entries are hidden for now. Roadmap:

- stabilize the minimal Humanize PPT output loop;
- tune multi-style showcase quality;
- finish presenter notes, navigation, and control experience;
- restore live demo entries after the workflows are stable.

## What it is not

- Not a generic PPT generator.
- Not a fixed bundle of several HTML PPT skills.
- Not a normal text humanizer.
- Not a guizang/Zara template converter.

## License

MIT
