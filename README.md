<div align="center">

# Humanize PPT

## 基于 AST 理论的人感 PPT 大纲导演 Skill

**先把资料变成人愿意听的大纲，再交给HTML PPT Skill做风格探索，生成页面，做演讲模式和部署上线**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[在线预览](https://learnprompt.github.io/humanize-ppt/) · [English](README.en.md) · [AST 理论](docs/AST-theory.md) · [OPC 工作流](docs/OPC-workflow.md) · [Agent Teams](docs/agent-teams.md)

</div>

---

## 这是什么

Humanize PPT 是一个 **PPT 大纲导演**，不是又一个HTML PPT模板库，也不是普通的文本润色工具。

用 AST 理论把原始资料拆成：

- 观众是谁；
- 观众看之前是什么状态；
- 看完以后应该变成什么状态；
- 中间最大的认知张力是什么；
- 每一页如何推动状态转移；

然后再把这份干净的生产说明书交给下游Skill生成HTML PPT和视频，比如op7418/guizang-ppt-skill、zarazhangrui/frontend-slides、heygen-com/hyperframes和lewislulu/html-ppt-skill

## 核心判断

> **PPT 不只是信息容器，而是观众状态改变器。**

AI 直接生成 PPT 时，容易出问题的地方已经不是页面不够漂亮了，模型把自己的解释过程、中间推理痕迹和结构噪音都写进了页面里。

Humanize PPT 的作用是先把资料“洗干净”，重组成一条适合讲解、适合演示、适合下游生成的观众路径。

## V0.5 能做什么

V0.5 在 **Selected Template Full Deck** 之后补齐 Presenter / Export Adapter：

```text
原始资料
→ Humanize PPT 生成 AST 生产契约
→ 自动选择 renderer 路由
→ 输出 commands/*.md 给下游专业 Agent
→ 可先跑 guizang 稳定 HTML deck，或接入 beautiful-html-templates 生成 3 个真实标题页预览
→ 用 --selected-template <slug> 把选中的 Beautiful 模板生成完整 deck
→ 用 --presenter-adapter 生成演讲者 shell 和逐页 notes
→ 用 --export-adapter 生成可移植HTML包和 PDF 导出脚本
→ 生成 run_manifest.json 和 QA 报告
```

当前包含：

- `SKILL.md`：Agent Skill 入口；
- `registry/renderer_registry.json`：下游 renderer 能力注册表；
- `docs/AST-theory.md`：AST 理论；
- `docs/OPC-workflow.md`：Outline / Produce / Complete 工作流；
- `contracts/`：输出契约模板与 schema；
- `scripts/humanize_ppt_v5.py`：V0.5 Presenter / Export Adapter 入口；
- `scripts/humanize_ppt_v4.py`：V0.4 Selected Template Full Deck 入口；
- `scripts/humanize_ppt_v3.py`：V0.3 Preview-First 入口；
- `scripts/humanize_ppt_v2.py`：V0.2 Router Edition 兼容 Runner；
- `scripts/humanize_ppt_v1.py`：V0.1 最小 Demo Runner；
- `examples/`：脱敏测试素材。

## 快速开始

```bash
git clone https://github.com/LearnPrompt/humanize-ppt.git
cd humanize-ppt

# 第一步：先看 3 个风格预览
python3 scripts/humanize_ppt_v3.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.3-preview \
  --title "AI 工具更新，不只是功能清单" \
  --style-mode preview-first

open .humanize-ppt-runs/ai-tool-update-v0.3-preview/outputs/beautiful/previews/index.html

# 第二步：选中一个模板后生成完整 deck，并补齐 presenter/export
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
open .humanize-ppt-runs/ai-tool-update-v0.5-complete/outputs/qa/qa_report.md
```

也可以显式指定 beautiful-html-templates 仓库路径：

```bash
python3 scripts/humanize_ppt_v5.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-v0.5-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter \
  --beautiful-repo /path/to/beautiful-html-templates
```

也可以跑 Hermes 安装讲解案例：

```bash
python3 scripts/humanize_ppt_v3.py \
  --source examples/02-hermes-install-guide/source.md \
  --out .humanize-ppt-runs/hermes-install-v0.3-preview \
  --title "把 Hermes 装成一个真正能干活的 Agent" \
  --style-mode preview-first
```

## 输出结果

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
    guizang-agent.md
    beautiful-agent.md
    html-ppt-agent.md
    frontend-slides-agent.md
    presenter-adapter-agent.md
    export-adapter-agent.md
    qa-agent.md
  outputs/
    guizang/
      index.html
      render_report.md
    beautiful/
      previews/
        index.html
        01-<slug>/index.html
        02-<slug>/index.html
        03-<slug>/index.html
      preview_manifest.json
      selected/
        index.html
      selected_manifest.json
      render_report.md
    presenter/
      index.html
      presenter_manifest.json
      render_report.md
    export/
      package/
        index.html
      export_pdf.sh
      export_manifest.json
      README.md
    qa/
      qa_report.md
      fix_list.md
      final_manifest.json
```

## 在线预览

- 首页：https://learnprompt.github.io/humanize-ppt/
- Skill 分享 PPT 展示页：https://learnprompt.github.io/humanize-ppt/showcase/skill-share/

风格探索、演讲者模式和其他生成模式还在调试中，公开入口先隐藏。Roadmap：

- 稳定 Humanize PPT 的最小输出链路；
- 调试多风格展示结果；
- 补齐演讲者模式的讲稿、翻页和控制体验；
- 完成后再恢复在线 Demo 入口。

## License

MIT
