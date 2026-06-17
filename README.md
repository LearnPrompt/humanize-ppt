<sub>🌐 <b>中文</b> · <a href="README.en.md">English</a></sub>

<div align="center">

# Humanize PPT

> *「所有人都在教 AI 把 PPT 渲染得好看，没人盯着它渲染完有多烂。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-humanize--ppt-blueviolet)](SKILL.md)
[![skills.sh](https://skills.sh/b/LearnPrompt/humanize-ppt)](https://skills.sh/LearnPrompt/humanize-ppt)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**面向 Agent 的 PPT 渲染质检员。上半场把资料编排成 AST 大纲加逐页素材决定的简报，交给下游 PPT Skill 100% 原生渲染；下半场做演讲体检（即此前的 QA 循环，CLI 仍是 `--qa-from`）。演讲体检对的不是美观，是大纲：逐页核对渲染结果和大纲页的差异，把「只能看、不能讲」的页揪出来，直到每一页都拿得出口去讲。模板库负责渲染得好看，Humanize 负责渲染完有人盯。它自己不渲染。**

[看效果](#效果展示) · [演讲体检](#演讲体检把只能看不能讲的页揪出来) · [演讲大纲预览](#演讲大纲预览渲染之前先看一眼观众状态弧) · [风格画廊](#风格画廊渲染之前先比-4-张封面) · [30秒上手](#30-秒开始让-agent-安装并使用) · [触发方式](#触发方式) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界) · [在线预览](https://learnprompt.github.io/humanize-ppt/) · [AST理论](docs/AST-theory.md)

</div>

---

## 效果展示

### 中文路线：guizang-ppt-skill 原生渲染

<p align="center">
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-01.png" width="32%" />
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-05.png" width="32%" />
  <img src="examples/03-codex-guizang-native-ink-classic/preview-slide-10.png" width="32%" />
</p>

<p align="center"><sub>
▲ Guizang Ink Classic 已知合格品（10 页 / 86 个 data-anim / WebGL hero）。Humanize 出大纲简报和演讲体检，guizang-ppt-skill 原生渲染。
<a href="https://learnprompt.github.io/humanize-ppt/">在线翻完整 deck →</a>
</sub></p>

### 英文路线：beautiful-html-templates 原生渲染，2026-06-13 过完整演讲体检

<p align="center">
  <img src="docs/showcase/hermes-agent-mastery/en/ppt/assets/en-preview-slide-01.png" width="49%" />
  <img src="docs/showcase/hermes-agent-mastery/en/ppt/assets/en-preview-slide-02.png" width="49%" />
</p>

<p align="center"><sub>
▲ Hermes Agent Mastery 英文 deck（Neo-Grid Bold，11 页），beautiful-html-templates 原生渲染。这份 deck 真实跑完了演讲体检：静态扫描通过后，截图逐页复核发现页码徽章遮挡 9 页正文（观众会看到被截断的句子），修复后复检通过。逐轮记录见
<a href="docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md">体检记录</a>。
<a href="https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/en/ppt/">在线翻完整 deck →</a>
</sub></p>

Humanize PPT 不抢模板库的工作。它是**渲染质检员**：上半场做简报编排，把资料整理成 AST 大纲加逐页素材决定（要不要图、要不要 SVG 示意图、要不要 Remotion 视频），写一份 `*-production-prompt.md` 给下游 Skill 100% 原生渲染；下半场做演讲体检，逐页核对渲染结果和大纲页的差异，写 fix prompt 给下游重渲，3 轮封顶。Humanize 自己不出 HTML。

## 演讲体检：把「只能看、不能讲」的页揪出来

先说清楚什么叫失败的页。一页只有几个字，没把这页该说的意思说完；或者这页没有完成它承诺的观众状态转移，听众看完这页，状态没有从 A 到 B。这样的页不应该存在。大家很容易被 HTML 的多样式吸引，结果做出一页里面什么内容都没有的 deck，那只是适合拿来看的 HTML。我们要做的是拿来演讲的 PPT，演讲体检就是把这种页揪出来，并生成修复指令让下游 skill 重渲。

体检怎么对：不对美观，对大纲。Humanize 上半场产出的大纲里写了每一页的意图和观众状态转移，体检就拿渲染结果逐页跟它核差异。失败模式目录在 [references/qa-failure-modes.md](references/qa-failure-modes.md)，每条模式都写了「观众视角会看到什么」，比如占位残留就是观众在正式页面上看到 lorem、TODO 这样的字样。

真实案例（2026-06-13，英文 deck）：静态扫描通过之后，截图逐页复核发现页码徽章把 9 页的最后一行正文盖住了，观众看到的是「uires confirmation.」这样的断句。这正是「只能看、不能讲」的页。修复保持原视觉体系，只给被遮挡的文字留出空位，复检通过。完整逐轮记录在 [体检记录](docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md)。

| 体检前：页码徽章吃掉正文 | 体检后：每个字都拿得出口 |
|---|---|
| ![体检前,左下角页码徽章遮住正文,只剩 uires confirmation. 的断句](docs/showcase/hermes-agent-mastery/en/ppt/assets/qa-before-s05.png) | ![体检后,What requires confirmation. 完整可见](docs/showcase/hermes-agent-mastery/en/ppt/assets/qa-after-s05.png) |

<sub>▲ 同一页 S05 的左下角：修复前观众看到「uires confirmation.」，修复后是完整的「What requires confirmation.」。视觉体系一个像素没动。</sub>

如果你的 deck 被演讲体检抓到过值得示众的翻车（占位残留、Hero 背景丢失、布局 ID 乱编……见 [失败模式目录](references/qa-failure-modes.md)），欢迎提 issue 投稿。

## 演讲大纲预览：渲染之前，先看一眼观众状态弧

v0.7.0 起，Humanize 有了第一个自己的可截图产物。不是 PPT（渲染归下游），而是质检员的工作底稿：观众状态转移图。输入 `slide_plan.json`，输出一页零依赖单文件 HTML：每页一行「页号 → 观众进入状态 → 本页意图 → 离开状态」，顶部一条状态弧摘要。渲染之前人先过一眼：哪一页没有推动状态转移，哪一页在原地踏步，5 分钟看穿。

<p align="center">
  <img src="examples/04-preview-outline-ai-tool-update/preview-outline.png" width="92%" />
</p>

<p align="center"><sub>
▲ 真实产物：<code>examples/01-ai-tool-update/source.md</code> 跑 brief 模式得到的 <code>slide_plan.json</code>，再经 <code>scripts/preview_outline_html.py</code> 生成。文件在 <code>examples/04-preview-outline-ai-tool-update/</code>，可直接双击打开。
</sub></p>

它和 `--preview-outline`（markdown 版大纲检查点，v0.6.6 起内置）是同一道关的两种形态：markdown 给 Agent 读，这页 HTML 给人看、给截图。生成命令见下方「进阶用法」。

## 风格画廊：渲染之前，先比 4 张封面

v0.9 起，出大纲之前还有一道门：风格画廊。一句话——别让人盲选风格。Humanize 为主渲染器出 **≥4 个封面候选**（guizang 跨 Style A 三主题加 Style B 瑞士配色，四张视觉互异），每个候选写一条「只渲封面一页」的命令交给下游 skill 真渲，再拼一页零依赖的 `style_gallery.html` 把 4 张封面并排供人挑。挑中哪张，回灌它的命令把那个风格带进正常的大纲 → brief 流程。

封面由下游真渲，Humanize 只出 spec 和 command，自己不渲一个像素——和它一贯的边界一致。命令里对 Style A 的 WebGL hero 封面专门加了警告：静态 PNG 截图会捕获到空白（canvas 加载后才画首帧），以活页 `cover.html` 为准，小于 20KB 的 PNG 判为截图失败而非空封面（见[失败模式目录](references/qa-failure-modes.md)）。规格见 [references/style-gallery-spec.md](references/style-gallery-spec.md)。

<p align="center">
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-ink-classic.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-kraft-paper.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-indigo-porcelain.png" width="24%" />
  <img src="docs/showcase/v0.9-style-gallery/covers/guizang-swiss-ikb.png" width="24%" />
</p>

<p align="center"><sub>
▲ 真实产物：同一份《AI 工具更新，不只是功能清单》的 4 张封面，由 guizang-ppt-skill 真渲——墨水经典 / 牛皮纸 / 靛蓝瓷（Style A）+ 瑞士克莱因蓝（Style B），四张视觉互异。Humanize 只出 spec/command，封面归下游渲。
</sub></p>

<p align="center">
  <img src="docs/showcase/v0.9-style-gallery/style-gallery-picker.png" width="80%" />
</p>

<p align="center"><sub>
▲ 零依赖 <code>style_gallery.html</code> 把 4 张封面并排供选，每张带描述和「选定后回灌命令」。挑中哪张，跑它的回灌命令把风格带进正常的大纲 → brief 流程。想要动图版录屏，用 <code>scripts/record_demo_gif.py</code>（见下方「进阶用法」）。
</sub></p>

生成命令见下方「进阶用法」。

## 30 秒开始：让 Agent 安装并使用

如果你正在使用 Codex、Claude Code、Hermes 或其他支持 Skill 的 Agent，先让它安装：

```text
请安装 Humanize PPT Skill：https://github.com/LearnPrompt/humanize-ppt
```

然后按三步走，每步一句话，直接复制发给 Agent。

**中文 PPT（推荐 guizang-ppt-skill 渲染）：**

第一步：

```text
把这份材料做成中文演讲 PPT，先用 humanize-ppt 出大纲和每页意图。
```

第二步：

```text
按这份大纲，用 guizang-ppt-skill 渲染成 deck。
```

第三步：

```text
渲染完跑一遍演讲体检，告诉我哪几页只能看不能讲，给出修复指令。
```

**英文 PPT（推荐 frontend-slides 或 beautiful-html-templates 渲染）：**

第一步：

```text
把这份材料做成英文演讲 PPT，先用 humanize-ppt 出大纲和每页意图。
```

第二步：

```text
按这份大纲，用 frontend-slides 或 beautiful-html-templates 渲染成 deck。
```

第三步：

```text
渲染完跑一遍演讲体检，告诉我哪几页只能看不能讲，给出修复指令。
```

记住那句定语：演讲体检对的不是美观，是大纲。逐页核对渲染结果和大纲页的差异，把「只能看、不能讲」的页揪出来，直到每一页都拿得出口去讲。

如果你的 Agent 需要明确安装命令，可以让它执行：

```bash
npx skills add LearnPrompt/humanize-ppt -g
```

Claude Code 用户也可以走 plugin marketplace（自动更新）：

```text
/plugin marketplace add LearnPrompt/humanize-ppt
/plugin install humanize-ppt
```

<details>
<summary><b>进阶用法</b>（CLI 参数、风格选择、fix prompt 细节，新手可以全部跳过）</summary>

### 给 Agent 的完整任务模板

```text
请安装并使用 Humanize PPT Skill（v0.9+）：
https://github.com/LearnPrompt/humanize-ppt

我要做一份 PPT。请按下面三步走，不要让 Humanize 自己渲染任何 HTML：

1. 用 Humanize PPT 生成 AST 大纲 + 逐页素材决定（要不要图、SVG、Remotion 视频）。
   它会输出 <renderer>-production-prompt.md。
2. 拿这份 prompt，调下游 skill 原生渲染：
   - 中文：guizang-ppt-skill，按 prompt 里指定的 Style（A/B）渲染
   - 英文：frontend-slides 或 beautiful-html-templates，原生模板选择 + 完整 deck
3. 渲染完后，用 Humanize PPT 跑演讲体检：
   python3 scripts/humanize_ppt.py --qa-from <rendered.html> --out <之前的 out 目录> --renderer guizang --guizang-style A --max-qa-iterations 3
   最多 3 轮，converge 就好，仍有问题就把 fix_prompt.md 转给下游 skill 重新渲染。
4. 体检通过后，让下游 skill 自己出 speaker notes / presenter shell / 部署。
```

### Brief 模式（默认）

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --guizang-style A
```

跑完会得到 `guizang-production-prompt.md`，**不会**有任何 `outputs/guizang/index.html` 之类的 HTML 产物。下一手交给 `guizang-ppt-skill` 渲染。英文路线把 `--renderer` 换成 `frontend-slides` 或 `beautiful-html-templates`。

### 演讲体检模式（拿到渲染产物后，CLI 即 `--qa-from`）

```bash
python3 scripts/humanize_ppt.py \
  --qa-from .humanize-ppt-runs/ai-tool-update/rendered/index.html \
  --out .humanize-ppt-runs/ai-tool-update \
  --renderer guizang \
  --guizang-style A \
  --max-qa-iterations 3
```

跑完会得到 `outputs/qa/qa_report.md` / `fix_prompt.md` / `qa_iteration.json`。第 3 轮仍 fail 就标 `needs-human` 停手。`fix_prompt.md` 是给下游 skill 的修复指令，直接转给它重渲，不要在 Humanize 里后处理 HTML。

### 演讲大纲预览（观众状态转移图）

```bash
python3 scripts/preview_outline_html.py \
  --slide-plan <out>/slide_plan.json \
  --out <out>/preview-outline.html \
  --title "你的 deck 标题"
```

### 风格画廊（v0.9，出大纲前的封面选择门）

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --style-gallery
```

会得到 `style_gallery.html`（4 张封面的零依赖选择器）、`style_gallery_plan.json` 和 `commands/style-gallery/<id>.md`（每个候选一条「只渲封面」命令）。下游按命令各渲一张封面到 `outputs/style-gallery/<id>/cover.{html,png}`，打开 `style_gallery.html` 挑一张，再跑该候选的回灌命令进入正常流程。`--gallery-count` 默认 4、最小 4，上限取该渲染器的候选数。

### 演示 GIF（工作底稿录制）

```bash
python3 scripts/record_demo_gif.py \
  --source examples/01-ai-tool-update/source.md \
  --title "你的 deck 标题" \
  --out docs/showcase/demo/humanize-ppt-demo.gif
```

把风格画廊 + 大纲预览两张零依赖工作底稿录成一支 GIF（需要 playwright + ffmpeg）。画廊封面由下游真渲，`--covers-dir <dir>` 可把真渲封面叠进画廊再录制；不给就录画廊的诚实待渲染态，不摆拍假缩略。

### 体检通过后怎么收尾

```text
体检 converged 之后，让 guizang-ppt-skill 自己出 speaker notes + presenter shell，
然后部署到 GitHub Pages 给我 URL。
```

</details>

## 触发方式

- 「帮我盯一下渲染出来的 PPT 有没有翻车」
- 「PPT 渲染质检」「给这份渲染好的 deck 做演讲体检」
- 「告诉我哪几页只能看不能讲」
- 「这页的 Hero 背景看不见，出修复指令让下游改」
- 「用 humanize-ppt 把这份资料做成 PPT 大纲」
- 「我有一堆笔记/录音转写，要做一份给产品团队看的 PPT」
- 「先出 AST 大纲和逐页素材决定，再调 guizang 渲染」
- 「把这份老 PPT 重新编排成人愿意听的结构」

按需求选路：只想要一页漂亮模板、不需要大纲和演讲体检时，直接用渲染类 skill 即可，比如 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)（中文）或 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) / [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)（英文）。要的是「观众听完状态有变化、每一页都拿得出口去讲」时，再加上 Humanize：渲染前的编排和渲染后的体检是它的活。

## 能力

- **AST 大纲**：把资料转成观众、状态转移、页面意图和讲述节奏。
- **逐页素材决定**：每页要不要图、要不要 SVG/HTML 示意图、要不要 Remotion 视频，Humanize 决定，下游 skill 原生产出。
- **生产简报**：写一份 `<renderer>-production-prompt.md` 给下游 skill 100% 原生渲染，不模仿、不 post-process。
- **演讲体检**：拿到渲染 HTML 后逐页核对渲染结果和大纲页的差异，扫失败模式（[references/qa-failure-modes.md](references/qa-failure-modes.md)），写 fix prompt 给下游 skill 重渲，最多 3 轮。
- **演讲大纲预览**：从 `slide_plan.json` 生成观众状态转移图（零依赖单文件 HTML），渲染之前人先过一眼状态弧。
- **风格画廊**（v0.9）：出大纲前先出 ≥4 个封面候选，下游各渲一张封面，拼一页零依赖选择器供人挑风格；挑中后回灌命令带进正常流程。Humanize 只出 spec/command，封面由下游真渲。

## 适合 / 不适合

适合：

- 你有资料、主题或大纲，需要 AST 大纲加逐页素材决定，再交付给原生下游 skill 渲染。
- 你希望渲染完有人逐页核对：哪页没说完意思、哪页没推动观众状态转移。
- 你希望中文 PPT 默认走 `guizang-ppt-skill`、英文走 `frontend-slides` / `beautiful-html-templates`，这是我们真实跑通的两条推荐路线。
- 你希望每次下游 skill 更新都不用改 Humanize：它只发 brief 不抄模板。

不适合：

- 你只想找一个单页模板库。
- 你希望 Humanize 自己渲染 HTML（这是 v0.6.4 起故意不做的事；下游 skill 才是渲染器）。
- 你还没明确主题、观众或交付场景。

## 它和同类有什么不同

| | 直接用模板库 Skill（guizang / frontend-slides） | **Humanize PPT** |
|---|---|---|
| 起点 | 资料直接进模板 | 先问观众是谁、看完要变成什么状态（AST） |
| 素材 | 模板自带什么用什么 | 逐页决定要不要图 / SVG / 视频，写进 brief |
| 渲染 | 自己渲染 | 100% 交给下游 Skill 原生渲染，零模仿 |
| 质量 | 渲染完即交付 | 演讲体检逐页核对大纲差异，最多 3 轮，写 fix prompt |
| 维护 | 模板更新要跟着改 | 下游更新零改动：只发 brief，不抄模板 |

一句话：模板库负责「渲染得好看」，Humanize 负责「有人听懂」加「渲染完有人盯」。它们是上下游，不是竞品。渲染是红海，渲染后的体检是空位，Humanize 站在空位上。

## 路线：热插拔，广义兼容，两条推荐

Humanize 的 brief 是普通 markdown + JSON，谁都能读。所以它**广义兼容任何能产出 HTML PPT 的下游 skill**：只要那个 skill 能按 brief 渲染出一份 HTML deck，Humanize 就能在前面发简报、在后面做演讲体检。下游是热插拔的，不存在绑定关系。

在这个前提下，我们把**真实跑通且输出稳定**的路线标出来作为推荐：

- **中文推荐一条**：`guizang-ppt-skill`（brief 出口 + 演讲体检都在真实渲染产物上验证过，support_level `full`）
- **英文推荐一条**：`frontend-slides` / `beautiful-html-templates`（两条都在真实 deck 上跑完了完整演讲体检，support_level `brief+qa-verified`——beautiful 2026-06-13、frontend-slides 2026-06-17）

其他下游可以接：把 brief 给任何渲染 skill 试一下，跑通了欢迎提 issue 反馈，我们据实更新 `registry/renderer_registry.json` 的 `support_level`。

工作流四段 O / P / Q / C：

- **O — Outline + Per-Page Media Direction**（Humanize）：raw material → AST 大纲 + 每页要不要图 / 视频
- **P — Native Renderer Invocation**（下游 skill 100%）：中文推荐 guizang-ppt-skill，英文推荐 frontend-slides / beautiful-html-templates，其他热插拔
- **Q — 演讲体检**（Humanize，CLI 即 `--qa-from`）：逐页核对大纲差异 → 写 fix_prompt.md → 等下游 skill 重渲 → 收敛，最多 3 轮
- **C — Complete**（下游 skill 原生）：speaker notes / presenter shell / 静态部署，**不属于 Humanize**

**多媒体边界**：视频或动态素材在 `slide_plan.json` 的 `media.video` 字段和 `video_slots.json` 里有决定，这两个字段维持不变，Humanize 继续逐页决定要不要视频、做什么用、多长。但**多媒体管线本身归下游**：Remotion / HyperFrames 的渲染、静态占位、嵌入方式都是下游 skill 的事，本仓库不修、不接管、不验证。

## 英文路径现状：照实说

对应 `registry/renderer_registry.json` 的 `support_level` 字段：

| 渲染器 | support_level | 实际含义 |
|---|---|---|
| `guizang-ppt-skill`（中文） | `full` | brief 出口 + 演讲体检都在真实渲染产物上验证过，失败模式目录有 7 条 guizang 规则 |
| `beautiful-html-templates`（英文） | `brief+qa-verified` | brief 出口可用；2026-06-13 在 `docs/showcase/hermes-agent-mastery/en/ppt/` 的真实 Neo-Grid deck 上完整跑通演讲体检（扫描 → 发现页码徽章遮挡 9 页正文 → 修复 → 复检通过，[逐轮记录](docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md)）；beautiful 专属失败模式规则仍为 0 条，故不升 full |
| `frontend-slides`（英文） | `brief+qa-verified` | brief 出口可用；2026-06-17 在第一单真实 frontend-slides deck（`docs/showcase/v0.9-frontend-slides/ppt/`，5 页单文件零依赖）上跑完演讲体检：静态扫描 pass + 负向对照证伪 + 截图逐页复核（[逐轮记录](docs/showcase/v0.9-frontend-slides/qa/presentation-checkup-2026-06-17.md)）；frontend-slides 专属失败模式规则仍为 0 条，故与 beautiful 同档、不升 full |

这不是承诺表，是实测表：每一格背后都要有真实渲染产物。空着的格子宁可空着，不摆拍。

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

演讲体检模式（CLI 即 `--qa-from`）会向 `outputs/qa/` 追加 `fix_prompt.md` 和 `qa_iteration.json`，最多 3 轮。

## 当前能力边界

- 推荐入口：`scripts/humanize_ppt.py`（演讲大纲预览：`scripts/preview_outline_html.py`）
- 历史版本说明：`docs/versions/`（v0.9 为什么改：`docs/versions/v0.9.0-style-gallery.md`）
- 版本计划与审查：`docs/plans/`
- 脱敏样例：`examples/`
- 中文已知合格品：`examples/03-codex-guizang-native-ink-classic/`
- 英文已体检样例：`docs/showcase/hermes-agent-mastery/en/`
- 渲染器支持级别：`registry/renderer_registry.json` 的 `support_level`（见上文实测表）

## 安全边界

- 不渲染、不 post-process 下游 Skill 的 HTML，渲染问题永远写成 fix prompt 交回下游改；
- 全流程本地脚本，零 API、零 Key，不外发任何资料内容；
- 演讲体检 3 轮不收敛即停手标注 `needs-human`，不无限重试；
- 不把私有路径、账号、凭据写进 brief 和示例。

## Reference

Humanize PPT 的设计参考了这些项目和操作规章：

- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)：中文稳定成稿、Swiss 风格约束、素材 QA。**Humanize 100% 调用它原生渲染，自己不抄模板。**
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)：英文路径的多风格候选和 selected-template full deck。
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)：英文 slide workflow、viewport-safe HTML deck、PPTX/发布方向。
- [huggingface/smolagents](https://github.com/huggingface/smolagents)：code-first Agent 工作流参考，帮助定义「Agent 读契约、执行工具、写回结果」的协作方式。
- [AST 理论](docs/AST-theory.md)、[OPC 工作流](docs/OPC-workflow.md)：Humanize PPT 自己的大纲方法、路由规则和执行边界。
- [SPEC.md](SPEC.md)（引擎技术规格）、[v0.9 版本说明](docs/versions/v0.9.0-style-gallery.md)、[风格画廊规约](references/style-gallery-spec.md)、[v0.8.0 版本说明](docs/versions/v0.8.0-presentation-checkup.md)、[v0.7.0 版本说明](docs/versions/v0.7.0-render-qa-inspector.md)、[v0.6.4 版本说明](docs/versions/v0.6.4-guizang-production-brief-orchestrator.md)、[brief 规约](references/guizang-production-brief-orchestrator.md)、[演讲体检失败模式](references/qa-failure-modes.md)：简报编排 + 演讲体检的契约，和质检员定位的来由。

## License

MIT

---

<div align="center">

**[LearnPrompt](https://github.com/LearnPrompt) 出品** · 同门手艺

[鲁班·Skill打磨](https://github.com/LearnPrompt/luban-skill) · [庖丁·博主蒸馏](https://github.com/LearnPrompt/paoding-skill) · [蔡伦·对话造纸](https://github.com/LearnPrompt/cailun-skill) · [阿福·LLM Todo](https://github.com/LearnPrompt/afu-llm-todo) · [AI雷达·零API资讯](https://github.com/LearnPrompt/ai-news-radar) · [淘金小镇·ClawHub日榜](https://github.com/LearnPrompt/skillrush-town) · [Irasutoya·正文配图](https://github.com/LearnPrompt/carl-irasutoya-illustrations) · [Humanize PPT·简报编排](https://github.com/LearnPrompt/humanize-ppt) · [CC Harness·六件套](https://github.com/LearnPrompt/cc-harness-skills)

<sub>公众号「卡尔的AI沃茨」 · [X @aiwarts](https://x.com/aiwarts) · [learnprompt.pro](https://www.learnprompt.pro)</sub>

</div>
