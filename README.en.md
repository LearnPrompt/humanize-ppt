<div align="center">

# Humanize PPT

## AST-based outline director Skill for human-centered AI presentation workflows

**Turn raw material into an audience-aware deck brief before handing it to compatible PPT / HTML PPT skills.**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[Live Demo](https://learnprompt.github.io/humanize-ppt/) · [中文](README.md) · [AST Theory](docs/AST-theory.md) · [OPC Workflow](docs/OPC-workflow.md) · [WorkBuddy Team Agent](docs/workbuddy-team-agent.md)

</div>

---

## What is this?

Humanize PPT is an **outline director Skill** for presentation workflows. It is not another slide template, not a normal text humanizer, and not an Agent hard-wired to four downstream skills.

It uses AST theory to turn raw material into a structured production brief:

- who the audience is;
- what state they are in before the deck;
- what state they should reach after the deck;
- what the core cognitive tension is;
- how each slide moves the audience forward;
- which downstream renderer or adapter should finish the job.

The clean brief can then be passed to compatible downstream tools. Guizang, Zara / frontend-slides, HyperFrames, and presenter-mode skills are recommended examples, not hard dependencies.

## Core idea

> **PPT is not an information container. PPT is an audience state-transfer artifact.**

When AI generates slides directly from raw material, the problem is often not visual quality. The bigger problem is that reasoning traces, explanatory noise, summary voice, and bloated structure leak into the deck.

Humanize PPT cleans and reorganizes the material into a presentation path before slide rendering starts.

## WorkBuddy Team Agent packaging

In this repository, Humanize PPT remains a Skill. For Tencent WorkBuddy, the right package shape is a Team Agent that includes this Skill and wraps it with role-specific agents:

```text
WorkBuddy Team Agent
├── Lead Agent: creates the team, dispatches members, and assembles delivery
├── Outline Director Agent: loads the humanize-ppt Skill and produces AST contracts
├── Renderer Agent: loads a selected or recommended PPT / HTML PPT Skill
├── Presenter Agent: adds presenter mode and speaker notes after the deck is finalized
└── QA Agent: verifies narrative, human feel, assets, paths, and delivery readiness
```

See: [WorkBuddy Team Agent packaging](docs/workbuddy-team-agent.md)

## V0.1 public preview

V0.1 validates a minimal loop:

```text
Raw material
→ Humanize PPT / AST Outline Director Skill
→ Compatible PPT / HTML PPT skill for style exploration and rendering
→ Presenter Adapter or presenter-mode skill
→ Static deploy package
```

It includes:

- `SKILL.md` — agent skill entrypoint;
- `docs/AST-theory.md` — AST theory;
- `docs/OPC-workflow.md` — Outline / Produce / Complete workflow;
- `docs/workbuddy-team-agent.md` — Tencent WorkBuddy Team Agent packaging plan;
- `contracts/` — output contract templates;
- `scripts/humanize_ppt_v1.py` — deterministic local demo runner;
- `examples/` — safe sample inputs.

## Quick start

```bash
git clone https://github.com/LearnPrompt/humanize-ppt.git
cd humanize-ppt

python3 scripts/humanize_ppt_v1.py   --source examples/01-ai-tool-update/source.md   --out .humanize-ppt-runs/ai-tool-update   --title "AI 工具更新，不只是功能清单"

open .humanize-ppt-runs/ai-tool-update/styles/index.html
open .humanize-ppt-runs/ai-tool-update/presenter/index.html
```

Run the Hermes installation explainer demo:

```bash
python3 scripts/humanize_ppt_v1.py   --source examples/02-hermes-install-guide/source.md   --out .humanize-ppt-runs/hermes-install   --title "把 Hermes 装成一个真正能干活的 Agent"
```

## Live demos

- Home: https://learnprompt.github.io/humanize-ppt/
- AI tool update style exploration: https://learnprompt.github.io/humanize-ppt/demo/styles/index.html
- AI tool update presenter mode: https://learnprompt.github.io/humanize-ppt/demo/presenter/index.html
- Hermes install style exploration: https://learnprompt.github.io/humanize-ppt/demo/hermes-install/styles/index.html
- Hermes install presenter mode: https://learnprompt.github.io/humanize-ppt/demo/hermes-install/presenter/index.html

## What it is not

- Not a generic PPT generator.
- Not a fixed bundle of several HTML PPT skills.
- Not a WorkBuddy Agent by itself; the Team Agent is a packaging layer around this Skill.
- Not a guizang/Zara template converter.

## License

MIT
