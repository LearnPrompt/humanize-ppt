# Humanize PPT V0.2 升级判断与版本建议

更新时间：2026-05-19 17:47 CST

## 结论

建议更新 Humanize PPT 版本。

但更新方向不应是把 Humanize PPT 做成又一个固定视觉模板 Skill，而是把它从当前的「AST 大纲导演 Demo」升级为「可独立调用的 PPT 总控 Skill」。

所谓「可独立运作」应定义为：用户只调用 Humanize PPT，它能完成从原始素材到最终 HTML PPT 的端到端调度；但实际渲染仍通过适配器调用 guizang、html-ppt、frontend-slides、beautiful-html-templates 等下游能力。

## 当前 Humanize PPT 状态

本地 Skill 路径：`/Users/carl/.hermes/skills/humanize-ppt`

当前 `SKILL.md` 版本：`0.1.0`

当前定位：

- Humanize PPT 是 Outline Director / Agent Teams Orchestrator，不是 slide renderer。
- 固定产出契约：`deck_brief.md`、`ast_outline.md`、`slide_plan.json`、`speaker_intent.md`、`asset_manifest.md`、`video_slots.json`。

当前脚本：`scripts/humanize_ppt_v1.py`

脚本验证结果：可运行，会生成 contract、3 个 demo style HTML、presenter、deploy 文件夹。但它仍是 demo 级实现：

- 5 页叙事角色写死：hook / conflict / method / proof / takeaway。
- 3 个视觉方向写死：guizang-stable / zara-editorial / zara-contrast。
- 没有真实读取下游 Skill 的模板库。
- 没有 renderer router。
- 没有把 `slide_plan.json` 实际交给 guizang/html-ppt/frontend-slides/beautiful 渲染。
- 没有统一 QA、截图、PDF、部署闭环。

## 上游/下游仓库近期变化

### 1. op7418/guizang-ppt-skill

GitHub 最新 pushed_at：2026-05-16T02:37:58Z

最新提交要点：

- `3d87acc6` Add bundled screenshot backgrounds
- `2b9e6be0` Add screenshot framing semantics
- `fd860dce` Add skill provenance marker
- `0338705b` Add hosted theme preview tables

本地安装状态：`/Users/carl/.agents/skills/guizang-ppt-skill`，文件数 34；已包含 `references/screenshot-framing.md` 和 `assets/screenshot-backgrounds/...`，基本是最新能力形态。

对 Humanize PPT 的影响：

- guizang 已经不只是网页 PPT 模板，还包括截图美化、配图提示、瑞士风版式锁、主题预览和质量检查。
- Humanize PPT V0.2 应把 guizang 作为「中文稳定渲染 + 截图/配图适配」适配器，而不是简单写成一个推荐 Skill。

### 2. zarazhangrui/beautiful-html-templates

GitHub 最新 pushed_at：2026-05-19T01:24:56Z

最新提交要点：

- `68ae471e` Add design.md for all 34 templates
- 近期修复 deck-stage hash navigation、screenshot renderer 等问题。

仓库能力：

- 34 个 HTML slide templates。
- `index.json` 提供 template_count、mood、occasion、tone、formality、density、scheme 等匹配字段。
- `AGENTS.md` 明确要求先按 occasion + mood 选 3 个候选模板，生成真实标题页 preview，让用户选，再做完整 deck。
- 每个模板新增 `design.md`，可作为结构化视觉契约。

对 Humanize PPT 的影响：

- 这是最适合补齐「风格探索」的库。
- Humanize PPT V0.2 应新增 `beautiful-template-router` 适配器：读取 `index.json`，按 AST 中的 audience / state / mood / density 选 3 个模板，生成 preview，再进入全 deck。
- 它不一定要安装成 Hermes Skill，但应该进入 Humanize PPT 的 renderer registry。

### 3. zarazhangrui/frontend-slides

GitHub 最新 pushed_at：2026-05-14T22:40:38Z；代码提交集中在 2026-04-08 前后。

仓库能力：

- 视觉风格 discovery：生成 3 个 style previews。
- PPTX 转 HTML。
- Vercel deploy + PDF export。
- Claude Code marketplace support。

本地安装状态：`/Users/carl/.agents/skills/frontend-slides`，包含 `STYLE_PRESETS.md`、`viewport-base.css`、`html-template.md`、`animation-patterns.md`、scripts。

对 Humanize PPT 的影响：

- frontend-slides 更像「从零生成/从 PPTX 转换」的完整 Skill。
- Humanize PPT 可借鉴它的 style discovery 与 viewport fitting 规则，但不应完全绑定它。

### 4. lewislulu/html-ppt-skill

GitHub 最新 pushed_at：2026-04-26T07:13:39Z

仓库能力：

- 36 themes。
- 15 full-deck templates。
- 31 page layouts。
- 47 animations（27 CSS + 20 canvas FX）。
- presenter mode：S 键打开 current / next / speaker script / timer 四卡片演讲者窗口。

本地安装状态：`/Users/carl/.hermes/skills/html-ppt`，文件数 226；已包含 `references/presenter-mode.md` 和 `templates/full-decks/presenter-mode-reveal/index.html`。

对 Humanize PPT 的影响：

- html-ppt 是最适合承担「端到端可交付 HTML PPT + presenter mode」的下游 Skill。
- Humanize PPT V0.2 应把 speaker_intent / 逐字稿转成 html-ppt 的 `<div class="notes">...</div>` 或 presenter-mode template 输入。

## 推荐版本路线

### V0.2：Humanize PPT Router Edition

目标：让 Humanize PPT 能被单独调用，并自动选择下游渲染路径。

最小交付：

1. `renderer_registry.json`
   - `guizang`
   - `html-ppt`
   - `frontend-slides`
   - `beautiful-html-templates`

2. `router_plan.json`
   - 输入：AST contract + 用户约束。
   - 输出：推荐 renderer、候选 style/template、风险提示、所需素材。

3. `commands/<renderer>.md`
   - 给下游 Skill/Agent 的有界命令，不让 renderer 直接吞原始素材。

4. `run_manifest.json`
   - 记录每次运行的 source、contracts、renderer、输出路径、QA 状态。

5. 更新 `SKILL.md`
   - 保持核心定位：Humanize PPT 是总控/导演，不是固定 renderer。
   - 明确「单独运作」含义：一键调度，不是自己承担所有渲染。

### V0.3：Standalone Skill UX

目标：形成用户可复制的一条命令。

建议 CLI：

```bash
python3 scripts/humanize_ppt.py \
  --source input.md \
  --out runs/my-deck \
  --title "Deck Title" \
  --renderer auto \
  --style-mode preview-first \
  --presenter on \
  --export html,pdf
```

最小交付：

- 自动产出 AST contracts。
- 自动选择/生成 3 个风格候选 preview。
- 用户选定后生成最终 deck。
- 自动跑 QA：viewport、缺图、路径、notes、导航、截图。
- 可选 PDF / deploy。

### V0.4：Agent Teams / WorkBuddy Package

目标：把 Humanize PPT 作为一个团队包，而不是单个脚本。

最小交付：

- Team Lead Agent。
- Outline Director Agent。
- Renderer Adapter Agents。
- QA Agent。
- Scenario rules。
- WorkBuddy/CodeBuddy upload zip 结构验证。

## 推荐路由规则

| 用户目标 | 推荐路径 |
|---|---|
| 中文分享、观点表达、稳定出片 | Humanize PPT → guizang |
| 瑞士风、方法论、数据/结构表达 | Humanize PPT → guizang Style B |
| 想看多个视觉方向再选 | Humanize PPT → beautiful-html-templates previews |
| 需要演讲者模式、逐字稿、主题/动画丰富 | Humanize PPT → html-ppt |
| 已有 PPTX，要转换成 Web PPT | Humanize PPT → frontend-slides |
| 要最终公开视频/素材片段 | Humanize PPT → HyperFrames / Remotion 作为素材生产器，不替代 PPT |

## 关键产品判断

Humanize PPT 不应该和 guizang、html-ppt、frontend-slides、beautiful-html-templates 竞争。

它应该站在它们上面：

- 负责判断观众。
- 负责删噪音。
- 负责把资料变成可讲路径。
- 负责把 AST 变成下游 renderer 可执行的生产契约。
- 负责把最终 deck 做 QA 和交付。

一句话版本：

> Humanize PPT V0.2 要从「会生成 demo 的大纲导演」升级为「能单独调用、自动调度多个 PPT Skill 的总控 Skill」。
