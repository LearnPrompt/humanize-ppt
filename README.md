<sub>🌐 <b>中文</b> · <a href="README.en.md">English</a></sub>

<div align="center">

# Humanize PPT

> *「PPT 不只是信息容器，而是观众状态改变器。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-humanize--ppt-blueviolet)](SKILL.md)
[![skills.sh](https://skills.sh/b/LearnPrompt/humanize-ppt)](https://skills.sh/LearnPrompt/humanize-ppt)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**面向 Agent 的 PPT 简报编排器：先把资料变成人愿意听的 AST 大纲 + 逐页素材决定，交给下游 PPT Skill 100% 原生渲染，再用 QA 循环盯住渲染结果。Humanize 自己不渲染。**

[看效果](#效果展示) · [30秒上手](#30-秒开始让-agent-安装并使用) · [触发方式](#触发方式) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界) · [在线预览](https://learnprompt.github.io/humanize-ppt/) · [AST理论](docs/AST-theory.md)

</div>

---

## 效果展示

Humanize PPT 不抢模板库的工作。它是**简报编排器**：把资料整理成 AST 大纲 + 逐页素材决定（要不要图、要不要 SVG 示意图、要不要 Remotion 视频），写一份 `*-production-prompt.md` 给下游 Skill 100% 原生渲染，最后用 QA 循环盯住渲染结果。Humanize 自己不出 HTML。

`examples/03-codex-guizang-native-ink-classic/` 是一份**已知合格的 Guizang Style A / Ink Classic 原生成品**（10 页、86 个 `data-anim`、WebGL hero 背景）。它不是 Humanize 的产物——是 `guizang-ppt-skill` 跑出来的，作为 QA 循环的视觉基准。

> 这一页 deck 是 guizang-ppt-skill 原生产物，Humanize 只负责出 brief 和 QA。

## 30 秒开始：让 Agent 安装并使用

如果你正在使用 Codex、Claude Code、Hermes 或其他支持 Skill 的 Agent，把这段话发给它：

```text
请安装并使用 Humanize PPT Skill（v0.6.5+）：
https://github.com/LearnPrompt/humanize-ppt

我要做一份 PPT。请按下面三步走，不要让 Humanize 自己渲染任何 HTML：

1. 用 Humanize PPT 生成 AST 大纲 + 逐页素材决定（要不要图、SVG、Remotion 视频）。
   它会输出 <renderer>-production-prompt.md。
2. 拿这份 prompt，调下游 skill 原生渲染：
   - 中文：guizang-ppt-skill，按 prompt 里指定的 Style (A/B) 渲染
   - 英文：frontend-slides 或 beautiful-html-templates，原生模板选择 + 完整 deck
3. 渲染完后，再用 Humanize PPT 跑 QA 循环：
   python3 scripts/humanize_ppt.py --qa-from <rendered.html> --out <之前的 out 目录> --renderer guizang --guizang-style A --max-qa-iterations 3
   最多 3 轮，converge 就好，仍有问题就改 prompt 让下游 skill 重新渲染。
4. QA 通过后，让下游 skill 自己出 speaker notes / presenter shell / 部署。

请确认 humanize-ppt、guizang-ppt-skill（或 frontend-slides / beautiful-html-templates）都可用。
Humanize 不再模仿任何下游 skill——它只发 brief 和盯 QA。
```

如果你的 Agent 需要明确安装命令，可以让它执行：

```bash
npx skills add https://github.com/LearnPrompt/humanize-ppt.git -g -y
```

## 怎么跟 Agent 交流

当前的对话模型是「Humanize 发 brief → 下游 skill 原生渲染 → Humanize 盯 QA」。你按这个循环给 Agent 下任务：

```text
我有一份关于「AI 工具更新」的资料，请用 Humanize PPT 出 AST 大纲 + 逐页素材决定，
目标是让产品团队理解这些工具会改变工作流。
```

```text
brief 看起来 OK。请按 prompt 调 guizang-ppt-skill 原生渲染中文 deck（Style A）。
渲染完用 Humanize PPT --qa-from 跑 QA，最长 3 轮。
如果某一页 Hero 背景看不见（WebGL 被遮），就把 fix_prompt.md 转给 guizang-ppt-skill 让它改。
```

```text
QA converged 之后，让 guizang-ppt-skill 自己出 speaker notes + presenter shell，
然后部署到 GitHub Pages 给我 URL。
```

## CLI 复现方式

### Brief 模式（默认）

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --guizang-style A
```

跑完会得到 `guizang-production-prompt.md`，**不会**有任何 `outputs/guizang/index.html` 之类的 HTML 产物。下一手交给 `guizang-ppt-skill` 渲染。

### QA 模式（拿到渲染产物后）

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update-v0.6.4/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update-v0.6.4 \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

跑完会得到 `outputs/qa/qa_report.md` / `fix_prompt.md` / `qa_iteration.json`。第 3 轮仍 fail → `needs-human`。

## 能力

- **AST 大纲**：把资料转成观众、状态转移、页面意图和讲述节奏。
- **逐页素材决定**：每页要不要图、要不要 SVG/HTML 示意图、要不要 Remotion 视频——Humanize 决定，下游 skill 原生产出。
- **生产简报**：写一份 `<renderer>-production-prompt.md` 给下游 skill 100% 原生渲染，不模仿、不 post-process。
- **QA 循环**：拿到渲染 HTML 后扫描失败模式（`references/qa-failure-modes.md`），写 fix prompt 给下游 skill 重渲，最多 3 轮。

## 适合 / 不适合

适合：

- 你有资料、主题或大纲，需要 AST 大纲 + 逐页素材决定 + 简报交付给原生下游 skill。
- 你希望中文 PPT 默认走 `guizang-ppt-skill` 原生成，Humanize 帮你盯 QA 循环。
- 你希望英文 PPT 走 `frontend-slides` / `beautiful-html-templates` 原生模板。
- 你希望每次下游 skill 更新都不用改 Humanize——它只发 brief 不抄模板。

不适合：

- 你只想找一个单页模板库。
- 你希望 Humanize 自己渲染 HTML（这是 v0.6.4 起故意不做的事；下游 skill 才是渲染器）。
- 你还没明确主题、观众或交付场景。

## 工作流路径

v0.6.4 起，工作流分成四段 O / P / Q / C：

- **O — Outline + Per-Page Media Direction**（Humanize）：raw material → AST 大纲 + 每页要不要图 / 视频
- **P — Native Renderer Invocation**（下游 skill 100%）：中文 guizang-ppt-skill、英文 frontend-slides / beautiful-html-templates
- **Q — Conversational QA Loop**（Humanize `--qa-from`）：扫失败模式 → 写 fix_prompt.md → 等下游 skill 重渲 → 收敛，最多 3 轮
- **C — Complete**（下游 skill 原生）：speaker notes / presenter shell / 静态部署，**不属于 Humanize**

Humanize PPT 当前重点是稳定「资料 → AST + 简报 → 下游 skill 原生 → QA 循环 → 部署」的工作流。视频或动态素材在 `slide_plan.json` 的 `media.video` 字段里有决定，下游 skill 按 prompt 原生产出 Remotion / 静态占位。

## 为什么是 AST

Humanize PPT 用 AST 理论把资料拆成：

- **Audience**：观众是谁，知道什么，抗拒什么；
- **State**：观众看之前是什么状态，看完以后应该变成什么状态；
- **Transfer**：每一页如何推动这次状态转移。

核心判断：

> PPT 不只是信息容器，而是观众状态改变器。

## 无依赖 smoke 验证

如果本机没有 pytest，也可以先跑标准库 smoke check：

```bash
python3 scripts/smoke_check.py
```

它会使用稳定入口跑一条不依赖外部模板库的最小链路，并检查这些关键文件：

```text
deck_brief.md
ast_outline.md
slide_plan.json
router_plan.json
run_manifest.json
outputs/qa/qa_report.md
guizang-production-prompt.md    ← v0.6.4 新增：必须存在
outputs/guizang/index.html       ← v0.6.4 新增：必须不存在
```

完整说明见：[docs/smoke-test.md](docs/smoke-test.md)。

## 输出结构

一次 brief 模式运行会生成：

```text
out/
  deck_brief.md
  ast_outline.md
  slide_plan.json            ← 每页带 media: {image, diagram, video} + layout_hint
  speaker_intent.md
  asset_manifest.md          ← 从 media 字段生成
  video_slots.json           ← 从 media.video 生成
  style_brief.md
  renderer_registry.json
  router_plan.json
  run_manifest.json
  guizang-production-prompt.md       ← v0.6.4 主交付物
  commands/
    guizang-agent.md
  outputs/
    qa/
      qa_report.md           ← 第一道关
```

QA 模式（`--qa-from`）会向 `outputs/qa/` 追加 `fix_prompt.md` 和 `qa_iteration.json`，最多 3 轮。

## 当前能力边界

- 推荐入口：`scripts/humanize_ppt.py`
- 历史版本说明：`docs/versions/`
- 版本计划与审查：`docs/plans/`
- 脱敏样例：`examples/`
- v0.6.4 已知合格品：`examples/03-codex-guizang-native-ink-classic/`

## Reference

Humanize PPT 的设计参考了这些项目和操作规章：

- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)：中文稳定成稿、Swiss 风格约束、素材 QA。**Humanize 100% 调用它原生渲染，自己不抄模板。**
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)：英文路径的多风格候选和 selected-template full deck。
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)：英文 slide workflow、viewport-safe HTML deck、PPTX/发布方向。
- [huggingface/smolagents](https://github.com/huggingface/smolagents)：code-first Agent 工作流参考，帮助定义「Agent 读契约、执行工具、写回结果」的协作方式。
- [AST 理论](docs/AST-theory.md)、[OPC 工作流](docs/OPC-workflow.md)：Humanize PPT 自己的大纲方法、路由规则和执行边界。
- [v0.6.4 版本说明](docs/versions/v0.6.4-guizang-production-brief-orchestrator.md)、[brief 规约](references/guizang-production-brief-orchestrator.md)、[QA 失败模式](references/qa-failure-modes.md)：v0.6.4 简报编排 + QA 循环的契约。

## License

MIT
