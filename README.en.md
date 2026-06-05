<div align="center">

# Humanize PPT

## PPT brief orchestrator for agents (v0.6.4)

**Turn raw material into an audience-aware AST outline + per-page media decisions, hand a production brief to a native downstream PPT skill, and run a post-render QA loop on the output. Humanize never renders HTML itself.**

[Live Preview](https://learnprompt.github.io/humanize-ppt/) · [Release](https://github.com/LearnPrompt/humanize-ppt/releases) · [MIT License](LICENSE)

[中文](README.md) · [AST Theory](docs/AST-theory.md) · [v0.6.4 Release Notes](docs/versions/v0.6.4-guizang-production-brief-orchestrator.md)

</div>

---

## Showcase

Humanize PPT is a **brief orchestrator**: it turns source material into an AST outline + per-page media decisions (image / SVG diagram / Remotion video / nothing), writes a `<renderer>-production-prompt.md`, and hands it to a downstream PPT skill that renders 100% natively. After rendering, Humanize runs a 3-iteration QA loop on the rendered HTML. It does **not** render HTML itself.

`examples/03-codex-guizang-native-ink-classic/` is the verified **known-good Guizang Style A / Ink Classic sample** (10 slides, 86 `data-anim`, WebGL hero background). It was produced by `guizang-ppt-skill`, not by Humanize — it serves as the visual baseline for the v0.6.4 QA loop.

> This deck is the native product of `guizang-ppt-skill`. Humanize only wrote the brief and ran the QA.

## 30-second start: ask your agent to install and use it

If you use Codex, Claude Code, Hermes, or another Skill-aware agent, send it this:

```text
Please install and use the Humanize PPT Skill (v0.6.4+):
https://github.com/LearnPrompt/humanize-ppt

I want to create a presentation. Follow these three steps. Do NOT let Humanize
render any HTML itself — that's the downstream skill's job.

1. Use Humanize PPT to produce the AST outline + per-page media decisions
   (image / SVG / Remotion video). It writes a <renderer>-production-prompt.md.

2. Take that prompt and invoke the downstream skill to render natively:
   - Chinese: guizang-ppt-skill, following the Style (A/B) in the prompt
   - English: frontend-slides or beautiful-html-templates, with their own
     template selection + full deck

3. After the deck is rendered, run the Humanize PPT QA loop on it:
   python3 scripts/humanize_ppt.py --qa-from <rendered.html> --out <out> \\
     --renderer guizang --guizang-style A --max-qa-iterations 3
   Max 3 rounds. Converge = done. If still failing, send the fix_prompt.md
   back to the downstream skill to re-render.

4. After QA passes, let the downstream skill produce its native speaker
   notes + presenter shell + deploy. Humanize does not own those.

Please confirm humanize-ppt, guizang-ppt-skill (or frontend-slides /
beautiful-html-templates) are all available. Humanize no longer imitates
any downstream skill — it only writes briefs and runs QA.
```

If your agent needs an explicit install command, ask it to run:

```bash
npx skills add https://github.com/LearnPrompt/humanize-ppt.git -g -y
```

## How to talk to the agent

The v0.6.4 conversational model is "Humanize writes a brief → downstream skill renders natively → Humanize runs QA". Drive the agent around this loop:

```text
I have material about "AI tool updates". Use Humanize PPT to produce the
AST outline + per-page media decisions. The audience is a product team.
The point is not a feature list; I want them to understand how these
tools change the workflow.
```

```text
The brief looks right. Hand it to guizang-ppt-skill and render the Chinese
deck natively (Style A). After rendering, run Humanize PPT --qa-from for
up to 3 rounds. If a hero page loses the WebGL background, send the
fix_prompt.md back to guizang-ppt-skill to re-render.
```

```text
After QA converges, ask guizang-ppt-skill to produce its native speaker
notes + presenter shell, then deploy to GitHub Pages and give me the URL.
```

## CLI reproduction

### Brief mode (default)

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --guizang-style A
```

You get `guizang-production-prompt.md`. **No** `outputs/guizang/index.html` is produced. Hand the prompt to `guizang-ppt-skill` to render.

### QA mode (post-render)

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update-v0.6.4/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

You get `outputs/qa/qa_report.md` / `fix_prompt.md` / `qa_iteration.json`. After 3 rounds with remaining failures → `needs-human`.

## What it does

- **AST outline**: audience, state transfer, slide intent, speaking rhythm.
- **Per-page media decision**: which page wants an image, a system diagram, a 10-second process clip, nothing.
- **Production brief**: a single `<renderer>-production-prompt.md` for the next agent. No template copy, no `SLIDES_HERE` injection, no post-process.
- **QA loop**: scans the rendered HTML for failure modes (`references/qa-failure-modes.md`), writes fix prompts for the downstream skill, max 3 rounds, then `needs-human`.

## Good fit / Not a fit

Good fit:

- You have source material, a topic, or a rough outline, and need an AST outline + per-page media decisions + a brief handoff to a native downstream skill.
- You want Chinese decks to default to `guizang-ppt-skill` natively, with Humanize watching the QA loop.
- You want English decks to go through `frontend-slides` / `beautiful-html-templates` native templates.
- You want Humanize to be immune to downstream skill updates — it only writes briefs, never imitates templates.

Not a fit:

- You only need a one-off template library.
- You expect Humanize to render HTML itself. (v0.6.4 deliberately does not — the downstream skill is the renderer.)
- You do not yet know the audience, topic, or delivery setting.

## Workflow paths

v0.6.4 splits the workflow into four stages O / P / Q / C:

- **O — Outline + Per-Page Media Direction** (Humanize): raw material → AST outline + per-page image / video decision
- **P — Native Renderer Invocation** (downstream skill 100%): Chinese `guizang-ppt-skill`, English `frontend-slides` / `beautiful-html-templates`
- **Q — Conversational QA Loop** (Humanize `--qa-from`): scan failure modes → write `fix_prompt.md` → wait for downstream re-render → converge, max 3 rounds
- **C — Complete** (downstream skill native): speaker notes / presenter shell / static deploy — **not owned by Humanize**

Humanize PPT's current focus is the stable "material → AST + brief → downstream native → QA loop → deploy" workflow. Video or motion material is decided in `slide_plan.json`'s `media.video` field; the downstream skill produces Remotion / static fallbacks per the brief.

## Why AST

Humanize PPT uses AST theory:

- **Audience**: who is listening, what they know, and what they resist;
- **State**: where the audience starts and where the deck should move them;
- **Transfer**: how each slide moves the audience forward.

Core idea:

> PPT is not an information container. PPT is an audience state-transfer artifact.

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
guizang-production-prompt.md    ← v0.6.4 new: must exist
outputs/guizang/index.html       ← v0.6.4 new: must NOT exist
```

See [docs/smoke-test.md](docs/smoke-test.md).

## Output shape

A brief-mode run produces:

```text
out/
  deck_brief.md
  ast_outline.md
  slide_plan.json            ← per-page media: {image, diagram, video} + layout_hint
  speaker_intent.md
  asset_manifest.md          ← derived from media
  video_slots.json           ← derived from media.video
  style_brief.md
  renderer_registry.json
  router_plan.json
  run_manifest.json
  guizang-production-prompt.md       ← v0.6.4 primary deliverable
  commands/
    guizang-agent.md
  outputs/
    qa/
      qa_report.md           ← first-pass gate
```

QA mode (`--qa-from`) appends `fix_prompt.md` and `qa_iteration.json` to `outputs/qa/`, max 3 rounds.

## Current boundaries

- Recommended entrypoint: `scripts/humanize_ppt.py`
- Historical version notes: `docs/versions/`
- Plans and reviews: `docs/plans/`
- Safe sample inputs: `examples/`
- v0.6.4 known-good: `examples/03-codex-guizang-native-ink-classic/`

## Reference

Humanize PPT is shaped by these projects and operating rules:

- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill): stable Chinese deck production, Swiss visual constraints, material QA. **Humanize invokes it 100% natively; it never copies its template.**
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates): English multi-style candidates and selected-template full deck production.
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides): English slide workflow, viewport-safe HTML decks, PPTX, and publishing direction.
- [huggingface/smolagents](https://github.com/huggingface/smolagents): a code-first agent workflow reference for the "read contract, run tools, write back results" collaboration pattern.
- [AST Theory](docs/AST-theory.md) and [OPC Workflow](docs/OPC-workflow.md): Humanize PPT's own outline method, routing model, and execution boundaries.
- [v0.6.4 Release Notes](docs/versions/v0.6.4-guizang-production-brief-orchestrator.md), [Brief Specification](references/guizang-production-brief-orchestrator.md), [QA Failure Modes](references/qa-failure-modes.md): the v0.6.4 brief-orchestrator + QA-loop contract.

## License

MIT
