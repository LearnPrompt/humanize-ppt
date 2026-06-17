<div align="center">

# Humanize PPT

## Render-QA inspector for agent-made PPTs (v0.9)

> *Everyone is teaching AI to render beautiful slides. Nobody is watching how badly they come out.*

**First half: turn raw material into an audience-aware AST outline plus per-page media decisions, and hand a production brief to a native downstream PPT skill. Second half: run the presentation checkup (演讲体检; formerly called the QA loop, the CLI flag is still `--qa-from`). The checkup does not grade beauty; it grades the outline: it compares every rendered page against its outline page, pulls out the pages that can only be looked at but not spoken from, and keeps going until every page is one you can stand up and present. Template skills own "looks good"; Humanize owns "someone checked". It never renders HTML itself.**

[Live Preview](https://learnprompt.github.io/humanize-ppt/) · [Release](https://github.com/LearnPrompt/humanize-ppt/releases) · [MIT License](LICENSE)

[中文](README.md) · [AST Theory](docs/AST-theory.md) · [v0.9 Release Notes](docs/versions/v0.9.0-style-gallery.md)

</div>

---

## Showcase

### Chinese route: rendered natively by guizang-ppt-skill

<p align="center">
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-01.png" width="32%" />
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-05.png" width="32%" />
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-10.png" width="32%" />
</p>

<p align="center"><sub>
▲ Verified known-good Guizang Ink Classic sample (10 slides, 86 data-anim, WebGL hero). Humanize wrote the brief and ran the checkup; guizang-ppt-skill rendered natively.
</sub></p>

### English route: rendered natively by beautiful-html-templates, full presentation checkup on 2026-06-13

<p align="center">
  <img src="docs/showcase/hermes-agent-mastery/en/ppt/assets/en-preview-slide-01.png" width="49%" />
  <img src="docs/showcase/hermes-agent-mastery/en/ppt/assets/en-preview-slide-02.png" width="49%" />
</p>

<p align="center"><sub>
▲ Hermes Agent Mastery English deck (Neo-Grid Bold, 11 slides), rendered natively by beautiful-html-templates. This deck went through a real presentation checkup: the static scan passed, then the page-by-page screenshot review caught the page-number badge cutting the last line of body text on 9 pages (the audience would see broken sentences); after the fix, the re-check passed. Round-by-round record:
<a href="docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md">checkup record</a>.
</sub></p>

Humanize PPT does not compete with template skills. It is a **render-QA inspector**: in the first half it orchestrates the brief, turning source material into an AST outline plus per-page media decisions (image / SVG diagram / Remotion video / nothing) and writing a `<renderer>-production-prompt.md` for a downstream PPT skill to render 100% natively. In the second half it runs the presentation checkup, comparing every rendered page against its outline page and writing fix prompts for the downstream skill, capped at 3 rounds. It does **not** render HTML itself.

## The presentation checkup: pulling out pages you can look at but cannot present

First, what counts as a failed page, in plain words. A page that holds only a few words and never finishes the point it was supposed to make; or a page that fails the audience state transfer it promised, so the listener walks out of that page in the same state they walked in. Such a page should not exist. It is easy to get seduced by the variety of HTML styles and end up with pages that contain almost nothing: that is HTML made for looking at. We are making PPTs for presenting. The presentation checkup exists to pull those pages out and generate fix instructions so the downstream skill can re-render them.

What the checkup compares against: not beauty, but the outline. The first half of Humanize produced an outline that states each page's intent and audience state transfer; the checkup walks the rendered deck page by page against it. The failure-mode catalog lives in [references/qa-failure-modes.md](references/qa-failure-modes.md); every mode states what the audience would see, for example placeholder residue means the audience sees literal lorem or TODO text on a live slide.

Real case (2026-06-13, the English deck above): after the static scan passed, the screenshot review found the page-number badge covering the last line of body text on 9 pages, so the audience would read fragments like "uires confirmation." That is exactly a page you can look at but cannot present. The fix kept the deck's visual system and only reserved clearance for the covered text; the re-check passed. Full round log: [checkup record](docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md).

| Before: the badge eats the body text | After: every word is presentable |
|---|---|
| ![Before the checkup, the page badge covers the body text, leaving the fragment "uires confirmation."](docs/showcase/hermes-agent-mastery/en/ppt/assets/qa-before-s05.png) | ![After the checkup, "What requires confirmation." is fully visible](docs/showcase/hermes-agent-mastery/en/ppt/assets/qa-after-s05.png) |

<sub>▲ Bottom-left corner of the same slide S05: "uires confirmation." before, the full "What requires confirmation." after. Not a single pixel of the visual system changed.</sub>

## Outline preview: see the audience state arc before rendering

Since v0.7.0, Humanize has its first screenshot-able artifact of its own. Not a deck (rendering stays downstream), but the inspector's worksheet: an audience state-transfer map. Input `slide_plan.json`, output a single-file zero-dependency HTML page, one row per slide ("slide id → state the audience walks in with → page intent → state they walk out with"), with a one-line state-arc summary on top. Five minutes of human review before any render happens.

<p align="center">
  <img src="examples/04-preview-outline-ai-tool-update/preview-outline.png" width="92%" />
</p>

<p align="center"><sub>
▲ Real artifact: <code>examples/01-ai-tool-update/source.md</code> run through brief mode produced the <code>slide_plan.json</code>; <code>scripts/preview_outline_html.py</code> rendered the map. Files live in <code>examples/04-preview-outline-ai-tool-update/</code>.
</sub></p>

It is the same checkpoint as `--preview-outline` (the built-in markdown outline review, since v0.6.6) in a second form: markdown for the agent to read, this HTML page for humans and screenshots. The command lives under "Advanced usage" below.

## Style gallery: compare 4 covers before rendering

Since v0.9, there is one more gate before the outline: the style gallery. In one line — don't make people pick a style blind. Humanize emits **≥4 cover candidates** for the primary renderer (guizang spans three Style A themes plus a Style B Swiss accent, so the four covers are visually distinct), writes one "render the cover only" command per candidate for the downstream skill to render for real, and stitches a zero-dependency `style_gallery.html` that places the 4 covers side by side to pick from. Pick one, and its re-injection command carries that style into the normal outline → brief flow.

The covers are rendered downstream; Humanize emits only the spec and the commands and renders not a single pixel — consistent with its standing boundary. The commands carry a specific warning for Style A WebGL hero covers: a static PNG screenshot can capture blank (the canvas paints its first frame after load), so treat the live `cover.html` as the source of truth and a sub-20KB PNG as a failed capture, not an empty cover (see the [failure-mode catalog](references/qa-failure-modes.md)). Spec: [references/style-gallery-spec.md](references/style-gallery-spec.md).

<p align="center">
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-ink-classic.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-kraft-paper.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-indigo-porcelain.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-swiss-ikb.png" width="24%" />
</p>

<p align="center"><sub>
▲ Real artifacts: four covers of the same deck, rendered natively by guizang-ppt-skill — Ink Classic / Kraft Paper / Indigo Porcelain (Style A) + Swiss Klein Blue (Style B), four distinct looks. Humanize emits only the spec/command; the covers are rendered downstream.
</sub></p>

<p align="center">
  <img src="docs/showcase/v0.9-style-gallery/style-gallery-picker.png" width="80%" />
</p>

<p align="center"><sub>
▲ The zero-dependency <code>style_gallery.html</code> places the 4 covers side by side, each with its description and re-injection command. Pick one and run its command to carry the style into the normal outline → brief flow. For a motion recording, use <code>scripts/record_demo_gif.py</code> (see "Advanced usage").
</sub></p>

The command lives under "Advanced usage" below.

## 30-second start: ask your agent to install and use it

If you use Codex, Claude Code, Hermes, or another Skill-aware agent, first have it install:

```text
Please install the Humanize PPT Skill: https://github.com/LearnPrompt/humanize-ppt
```

Then drive it in three steps, one plain sentence each, copy-paste ready.

**Chinese deck (recommended renderer: guizang-ppt-skill):**

Step 1:

```text
Turn this material into a Chinese presentation deck. Start with humanize-ppt to produce the outline and each page's intent.
```

Step 2:

```text
Following that outline, render the deck with guizang-ppt-skill.
```

Step 3:

```text
After rendering, run the presentation checkup. Tell me which pages can only be looked at but not presented, and give me the fix instructions.
```

**English deck (recommended renderer: frontend-slides or beautiful-html-templates):**

Step 1:

```text
Turn this material into an English presentation deck. Start with humanize-ppt to produce the outline and each page's intent.
```

Step 2:

```text
Following that outline, render the deck with frontend-slides or beautiful-html-templates.
```

Step 3:

```text
After rendering, run the presentation checkup. Tell me which pages can only be looked at but not presented, and give me the fix instructions.
```

Keep the one-liner in mind: the checkup does not grade beauty, it grades the outline. It compares every rendered page against its outline page, pulls out the pages that can only be looked at but not spoken from, until every page is one you can stand up and present.

If your agent needs an explicit install command, ask it to run:

```bash
npx skills add LearnPrompt/humanize-ppt -g
```

<details>
<summary><b>Advanced usage</b> (CLI flags, style selection, fix-prompt details; beginners can skip all of this)</summary>

### Full task template for the agent

```text
Please install and use the Humanize PPT Skill (v0.9+):
https://github.com/LearnPrompt/humanize-ppt

I want to create a presentation. Follow these three steps. Do NOT let Humanize
render any HTML itself — that's the downstream skill's job.

1. Use Humanize PPT to produce the AST outline + per-page media decisions
   (image / SVG / Remotion video). It writes a <renderer>-production-prompt.md.

2. Take that prompt and invoke the downstream skill to render natively:
   - Chinese: guizang-ppt-skill, following the Style (A/B) in the prompt
   - English: frontend-slides or beautiful-html-templates, with their own
     template selection + full deck

3. After the deck is rendered, run the Humanize PPT presentation checkup:
   python3 scripts/humanize_ppt.py --qa-from <rendered.html> --out <out> \
     --renderer guizang --guizang-style A --max-qa-iterations 3
   Max 3 rounds. Converge = done. If still failing, send the fix_prompt.md
   back to the downstream skill to re-render.

4. After the checkup passes, let the downstream skill produce its native
   speaker notes + presenter shell + deploy. Humanize does not own those.
```

### Brief mode (default)

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --guizang-style A
```

You get `guizang-production-prompt.md`. **No** `outputs/guizang/index.html` is produced. Hand the prompt to `guizang-ppt-skill` to render. For English routes, set `--renderer` to `frontend-slides` or `beautiful-html-templates`.

### Presentation checkup mode (post-render; the CLI flag is `--qa-from`)

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

You get `outputs/qa/qa_report.md` / `fix_prompt.md` / `qa_iteration.json`. After 3 rounds with remaining failures → `needs-human`. `fix_prompt.md` is downstream-skill-actionable: hand it back for a native re-render; never post-process the HTML in Humanize.

### Outline preview (audience state-transfer map)

```bash
python3 scripts/preview_outline_html.py \
  --slide-plan <out>/slide_plan.json \
  --out <out>/preview-outline.html \
  --title "Your deck title"
```

### Style gallery (v0.9, the cover-style gate before the outline)

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --style-gallery
```

You get `style_gallery.html` (a zero-dependency picker for the 4 covers), `style_gallery_plan.json`, and `commands/style-gallery/<id>.md` (one "cover only" command per candidate). The downstream skill renders one cover each to `outputs/style-gallery/<id>/cover.{html,png}`; open `style_gallery.html`, pick one, then run that candidate's re-injection command to resume the normal flow. `--gallery-count` defaults to 4, minimum 4, capped at the candidates defined for the renderer.

### Demo GIF (working-draft recording)

```bash
python3 scripts/record_demo_gif.py \
  --source examples/01-ai-tool-update/source.md \
  --title "Your deck title" \
  --out docs/showcase/demo/humanize-ppt-demo.gif
```

Records the style gallery + outline preview — the two zero-dependency working drafts — into one GIF (requires playwright + ffmpeg). The gallery covers are rendered downstream; `--covers-dir <dir>` overlays real rendered covers into the gallery before recording. Without it, the gallery records in its honest pending state — no faked thumbnails.

### After the checkup converges

```text
After the checkup converges, ask the downstream skill to produce its native
speaker notes + presenter shell, then deploy to GitHub Pages and give me the URL.
```

</details>

## What it does

- **AST outline**: audience, state transfer, slide intent, speaking rhythm.
- **Per-page media decision**: which page wants an image, a system diagram, a 10-second process clip, nothing.
- **Production brief**: a single `<renderer>-production-prompt.md` for the next agent. No template copy, no `SLIDES_HERE` injection, no post-process.
- **Presentation checkup**: compares every rendered page against its outline page, scans for failure modes (`references/qa-failure-modes.md`), writes fix prompts for the downstream skill, max 3 rounds, then `needs-human`.
- **Outline preview**: renders the audience state-transfer map (zero-dependency single-file HTML) from `slide_plan.json` for a human pass before any render.
- **Style gallery** (v0.9): before the outline, emits ≥4 cover candidates; the downstream skill renders one cover each; stitches a zero-dependency picker to choose a style, then a re-injection command carries the choice into the normal flow. Humanize emits only the spec/command; covers are rendered downstream.

## Good fit / Not a fit

Good fit:

- You have source material, a topic, or a rough outline, and need an AST outline plus per-page media decisions plus a brief handoff to a native downstream skill.
- You want someone to walk the rendered deck page by page: which page never finished its point, which page failed its audience state transfer.
- You want Chinese decks on `guizang-ppt-skill` and English decks on `frontend-slides` / `beautiful-html-templates`: the two routes we have actually run end to end with stable output.
- You want Humanize to be immune to downstream skill updates: it only writes briefs, never imitates templates.

Not a fit:

- You only need a one-off template library. Pick whichever need you have: if all you want is one beautiful template page, with no outline and no presentation checkup, just use a rendering skill directly.
- You expect Humanize to render HTML itself. (Deliberately not, since v0.6.4: the downstream skill is the renderer.)
- You do not yet know the audience, topic, or delivery setting.

## Routes: hot-pluggable, broadly compatible, two recommendations

The Humanize brief is plain markdown + JSON; anything can read it. So Humanize is **broadly compatible with any downstream skill that can produce an HTML PPT**: if a skill can render an HTML deck from the brief, Humanize can write the brief before it and run the presentation checkup after it. Downstream renderers are hot-pluggable; there is no binding.

On top of that, we mark the routes we have **actually run end to end with stable output** as recommendations:

- **One Chinese recommendation**: `guizang-ppt-skill` (brief exit + presentation checkup both verified on real rendered output; support_level `full`)
- **One English recommendation**: `frontend-slides` / `beautiful-html-templates` (the beautiful leg completed a full presentation checkup on a real deck on 2026-06-13, support_level `brief+qa-verified`; the frontend-slides checkup leg has not run on real output yet, so it stays `brief-only`)

Other downstreams are welcome: feed the brief to any rendering skill, and if it works, open an issue. We update `support_level` in `registry/renderer_registry.json` based on real results.

The workflow has four stages O / P / Q / C:

- **O — Outline + Per-Page Media Direction** (Humanize): raw material → AST outline + per-page image / video decision
- **P — Native Renderer Invocation** (downstream skill 100%): Chinese recommendation `guizang-ppt-skill`, English recommendation `frontend-slides` / `beautiful-html-templates`, others hot-pluggable
- **Q — Presentation checkup** (Humanize; the CLI flag is `--qa-from`): compare pages against the outline → write `fix_prompt.md` → wait for downstream re-render → converge, max 3 rounds
- **C — Complete** (downstream skill native): speaker notes / presenter shell / static deploy — **not owned by Humanize**

**Media boundary:** video and motion material is decided in `slide_plan.json`'s `media.video` field and `video_slots.json` — those decision fields stay. But the **media pipeline itself is downstream-owned**: Remotion / HyperFrames rendering, static fallbacks, and embedding are the downstream skill's job. This repo does not fix, take over, or verify that pipeline.

## English path, stated honestly

Matching the `support_level` field in `registry/renderer_registry.json`:

| Renderer | support_level | What it actually means |
|---|---|---|
| `guizang-ppt-skill` (Chinese) | `full` | Both the brief exit and the presentation checkup are verified on real rendered output; the failure-mode catalog has 7 guizang rules |
| `beautiful-html-templates` (English) | `brief+qa-verified` | Brief exit works; on 2026-06-13 a full presentation checkup ran on the real Neo-Grid deck at `docs/showcase/hermes-agent-mastery/en/ppt/` (scan → badge-overlap finding on 9 pages → fix → re-check pass, [round log](docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md)); still 0 renderer-specific failure-mode rules, so not `full` |
| `frontend-slides` (English) | `brief-only` | Brief exit works; the checkup leg has never run on a real frontend-slides render (the verified English deck above was rendered by beautiful-html-templates). Upgrades when the first real deck goes through |

This is a measurement table, not a promise table: every cell must be backed by real rendered output. Empty cells stay empty; nothing is staged.

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

Presentation-checkup mode (CLI `--qa-from`) appends `fix_prompt.md` and `qa_iteration.json` to `outputs/qa/`, max 3 rounds.

## Current boundaries

- Recommended entrypoint: `scripts/humanize_ppt.py` (outline preview: `scripts/preview_outline_html.py`)
- Historical version notes: `docs/versions/` (why v0.9: `docs/versions/v0.9.0-style-gallery.md`)
- Plans and reviews: `docs/plans/`
- Safe sample inputs: `examples/`
- Chinese known-good: `examples/03-codex-guizang-native-ink-classic/`
- English checked-up sample: `docs/showcase/hermes-agent-mastery/en/`
- Renderer support levels: `support_level` in `registry/renderer_registry.json` (see the table above)

## Reference

Humanize PPT is shaped by these projects and operating rules:

- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill): stable Chinese deck production, Swiss visual constraints, material QA. **Humanize invokes it 100% natively; it never copies its template.**
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates): English multi-style candidates and selected-template full deck production.
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides): English slide workflow, viewport-safe HTML decks, PPTX, and publishing direction.
- [huggingface/smolagents](https://github.com/huggingface/smolagents): a code-first agent workflow reference for the "read contract, run tools, write back results" collaboration pattern.
- [AST Theory](docs/AST-theory.md) and [OPC Workflow](docs/OPC-workflow.md): Humanize PPT's own outline method, routing model, and execution boundaries.
- [SPEC.md](SPEC.md) (engine technical specification), [v0.9 Release Notes](docs/versions/v0.9.0-style-gallery.md), [Style Gallery Spec](references/style-gallery-spec.md), [v0.8.0 Release Notes](docs/versions/v0.8.0-presentation-checkup.md), [v0.7.0 Release Notes](docs/versions/v0.7.0-render-qa-inspector.md), [v0.6.4 Release Notes](docs/versions/v0.6.4-guizang-production-brief-orchestrator.md), [Brief Specification](references/guizang-production-brief-orchestrator.md), [Presentation Checkup Failure Modes](references/qa-failure-modes.md): the brief-orchestrator + checkup contract, and why the inspector positioning exists.

## License

MIT

---

<div align="center">

**Made by [LearnPrompt](https://github.com/LearnPrompt)** · From the same workshop

[Luban · skill polishing](https://github.com/LearnPrompt/luban-skill) · [Paoding · blogger distilling](https://github.com/LearnPrompt/paoding-skill) · [Cailun · chat-to-page](https://github.com/LearnPrompt/cailun-skill) · [Afu · LLM todo](https://github.com/LearnPrompt/afu-llm-todo) · [AI News Radar · zero-API](https://github.com/LearnPrompt/ai-news-radar) · [Skillrush Town · ClawHub daily](https://github.com/LearnPrompt/skillrush-town) · [Irasutoya Illustrations](https://github.com/LearnPrompt/carl-irasutoya-illustrations) · [Humanize PPT](https://github.com/LearnPrompt/humanize-ppt) · [CC Harness](https://github.com/LearnPrompt/cc-harness-skills)

<sub>WeChat「卡尔的AI沃茨」 · [X @aiwarts](https://x.com/aiwarts) · [learnprompt.pro](https://www.learnprompt.pro)</sub>

</div>
