# Guizang Production Adapter Upgrade Brief

Date: 2026-05-31

## Context

Humanize PPT already has a public GitHub project at `LearnPrompt/humanize-ppt` and a public Pages site at:

- https://learnprompt.github.io/humanize-ppt/

The current showcase artifact is:

- `docs/showcase/codex-guizang-black-white/index.html`

It was generated from a local experiment in:

- `/Users/carl/Documents/Codex/2026-05-31/herems-profile-stepaux-stepflash/outputs/humanize-guizang-black-white-ppt/`

The experiment proved that Humanize PPT can:

- read a source deck brief with `目标页数：15-18 页`
- expand beyond the old 8-page cap
- render through `guizang-ppt-skill/assets/template-swiss.html`
- copy `assets/motion.min.js`
- emit `render_manifest.json`
- remove `[必填]` template residue
- record 16 `data-layout="Sxx"` markers and 10 unique layout IDs

But the user explicitly asked whether this is 1:1 Guizang quality. The answer is no. It is a useful intermediate adapter, not a full Guizang-native production pass.

## Current Quality Gap

The black-white showcase is roughly a 60%-70% Guizang adapter:

- It uses the real Swiss template.
- It has real layout markers.
- It has a watchable deck.
- It is not yet using the full registered `layouts-swiss.md` skeletons page by page.
- It does not run Guizang's Swiss validator.
- It does not perform screenshot-based visual QA.
- It does not produce the required page-by-page production reasoning: `page -> Sxx layout -> why this layout -> image/data slot -> validation result`.

## Goal

Upgrade Humanize PPT's Guizang path into a real production adapter while preserving existing `0.6.3` behavior:

- Do not regress English 5-style gallery behavior.
- Do not regress presenter bridge behavior.
- Do not regress Beautiful selected-template behavior.
- Do not regress existing tests.

The target architecture is:

```text
Humanize PPT
  -> AST contract
  -> Guizang production brief
  -> real Guizang Swiss generation
  -> Guizang validator
  -> screenshot / visual QA
  -> presenter adapter
  -> GitHub Pages showcase
```

## Workstreams

### 1. Codex Workstream

Use Codex for repo-safe implementation and verification.

Scope:

- `scripts/humanize_ppt_v2.py`
- `scripts/humanize_ppt.py`
- `tests/test_beautiful_preview.py`
- `tests/test_main_entrypoint.py`
- `docs/versions/`
- `references/`
- `docs/showcase/`

Tasks:

- Merge the local Guizang production-adapter experiment into current `0.6.3` without reverting newer behavior.
- Add CLI flags:
  - `--guizang-template auto|classic|swiss`
  - `--guizang-skill-root`
  - `--min-slides`
  - `--max-slides`
  - optional `--guizang-theme` if theme presets are formalized
- Add source parsing:
  - page-count hints like `15-18 页`
  - `建议页结构` numbered lists
  - per-page title/message extraction
- Add render metadata:
  - template slug
  - skill root
  - copied assets
  - layout IDs
  - layout count
  - fallback status
  - placeholder residue status
- Make QA fail on:
  - fallback template
  - too few slides
  - low layout diversity
  - remaining `[必填]`
  - mismatch between planned layout count and actual HTML markers
- Keep existing English style-gallery tests green.

Verification:

```bash
python3 -m py_compile scripts/humanize_ppt_v2.py
python3 -m pytest -q
python3 scripts/smoke_check.py
```

If local `pytest` is unavailable, use `scripts/smoke_check.py` plus targeted no-dependency Python smoke tests, and state that clearly.

### 2. Claude Code Workstream

Use Claude Code for Guizang fidelity and visual judgment.

Scope:

- read-only reference:
  - `/Users/carl/.agents/skills/guizang-ppt-skill/SKILL.md`
  - `/Users/carl/.agents/skills/guizang-ppt-skill/references/layouts-swiss.md`
  - `/Users/carl/.agents/skills/guizang-ppt-skill/references/swiss-layout-lock.md`
  - `/Users/carl/.agents/skills/guizang-ppt-skill/references/checklist.md`
  - `/Users/carl/.agents/skills/guizang-ppt-skill/assets/template-swiss.html`
- write targets in this repo:
  - `references/guizang-production-adapter.md`
  - `docs/versions/v0.6.4-guizang-production-adapter.md`
  - visual QA notes under `docs/showcase/codex-guizang-black-white/`

Tasks:

- Convert the current simplified layout generator into a Guizang-compatible production spec.
- Define a strict intermediate artifact:
  - `guizang_production_plan.json`
  - `page_layout_map.md`
  - `visual_qa_report.md`
- For every slide, require:
  - page number
  - chosen `Sxx`
  - why this layout fits the content
  - required slots
  - forbidden shortcuts
  - validation result
- Identify which generated slides violate Guizang Swiss locked mode.
- Recommend fixes using existing `S01-S22` registered layouts only.

Claude Code should not blindly rewrite the whole project. It should produce the Guizang fidelity spec and review notes, then Codex can wire them into the implementation.

## Acceptance Criteria

A future run should produce:

- `outputs/guizang/index.html`
- `outputs/guizang/render_manifest.json`
- `outputs/guizang/guizang_production_plan.json`
- `outputs/guizang/page_layout_map.md`
- `outputs/guizang/visual_qa_report.md`
- `outputs/qa/qa_report.md`

And these checks must pass:

- no `[必填]`
- no fallback template
- slide count respects source hints
- `data-layout="Sxx"` count equals slide count
- at least 6 unique Swiss layouts for 7-8 page decks, higher for longer decks
- no invented non-registered layout IDs
- presenter adapter can control the deck
- GitHub Pages showcase is accessible

## Current Showcase Evidence

Use this as the baseline artifact, not as the final quality target:

- `docs/showcase/codex-guizang-black-white/index.html`
- `docs/showcase/codex-guizang-black-white/reports/render_report.md`
- `docs/showcase/codex-guizang-black-white/reports/render_manifest.json`
- `docs/showcase/codex-guizang-black-white/reports/qa_report.md`

## Suggested Prompt For The Next Agent

```text
你要同时协调 Claude Code 和 Codex，升级 LearnPrompt/humanize-ppt 的 Guizang production adapter。

先读：
- docs/plans/2026-05-31-guizang-production-adapter-upgrade.md
- docs/showcase/codex-guizang-black-white/README.md
- scripts/humanize_ppt_v2.py
- tests/test_beautiful_preview.py
- /Users/carl/.agents/skills/guizang-ppt-skill/SKILL.md
- /Users/carl/.agents/skills/guizang-ppt-skill/references/layouts-swiss.md
- /Users/carl/.agents/skills/guizang-ppt-skill/references/swiss-layout-lock.md

目标：
把现在的 60%-70% Guizang adapter 升级成真正生产 adapter，但不要破坏 Humanize PPT 0.6.3 已有的 English 5-style gallery、presenter bridge、Beautiful selected-template 功能。

分工：
- Codex 负责 repo 内代码实现、测试、Pages showcase 更新、commit/push。
- Claude Code 负责 Guizang fidelity review：逐页检查是否符合 Swiss locked layouts，并输出 page_layout_map / visual_qa_report / 100% 还原所需规则。

先做小步提交，不要整文件覆盖。
```
