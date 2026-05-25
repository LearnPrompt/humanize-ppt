<div align="center">

# Humanize PPT

## 基于AST理论的人感PPT大纲导演Skill

**先把资料变成人愿意听的大纲，再交给HTML PPT Skill做风格探索、生成页面、补演讲模式和导出包。**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[在线预览](https://learnprompt.github.io/humanize-ppt/) · [English](README.en.md) · [AST理论](docs/AST-theory.md) · [OPC工作流](docs/OPC-workflow.md) · [Agent Teams](docs/agent-teams.md)

</div>

---

## 这是什么

Humanize PPT 是一个**PPT大纲导演**。它不直接充当模板库，也不把原始资料粗暴塞进页面，而是先生成一份适合讲解、适合演示、适合交给下游渲染器的生产契约。

它用AST理论把资料拆成：

- **Audience**：观众是谁，知道什么，抗拒什么；
- **State**：观众看之前是什么状态，看完以后应该变成什么状态；
- **Transfer**：每一页如何推动这次状态转移。

核心判断：

> PPT不只是信息容器，而是观众状态改变器。

## 快速开始

新用户只需要记住一个入口：

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-preview \
  --title "AI 工具更新，不只是功能清单" \
  --style-mode preview-first
```

查看结果：

```bash
open .humanize-ppt-runs/ai-tool-update-preview/outputs/beautiful/previews/index.html
open .humanize-ppt-runs/ai-tool-update-preview/outputs/qa/qa_report.md
```

如果已经选中一个Beautiful模板，可以继续生成完整deck，并补齐presenter/export：

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter
```

旧版`scripts/humanize_ppt_v1.py`到`scripts/humanize_ppt_v5.py`仍保留，用于兼容和历史复现；README只推荐`scripts/humanize_ppt.py`。

## 无依赖smoke验证

如果本机没有pytest，也可以先跑标准库smoke check：

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
```

完整说明见：[docs/smoke-test.md](docs/smoke-test.md)。

## 输出结构

一次运行会生成：

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

根据是否选择模板、是否启用presenter/export，部分输出目录可能为空或标记为待处理。

## 当前能力边界

- 推荐入口：`scripts/humanize_ppt.py`
- 兼容入口：`scripts/humanize_ppt_v1.py`到`scripts/humanize_ppt_v5.py`
- 历史版本说明：`docs/versions/`
- 版本计划与审查：`docs/plans/`
- 脱敏样例：`examples/`

Humanize PPT 当前重点是稳定“资料 → AST生产契约 → 风格预览/完整deck → presenter/export → QA”的工作流。更多renderer自动化、视频生成、部署平台集成和团队包上传会放到后续版本，不塞进这次目录整理。

## 在线预览

- 首页：https://learnprompt.github.io/humanize-ppt/
- Skill分享PPT展示页：https://learnprompt.github.io/humanize-ppt/showcase/skill-share/

风格探索、演讲者模式和其他生成模式还在调试中，公开入口先隐藏。稳定后再恢复在线Demo入口。

## 参考文档

- [AST理论](docs/AST-theory.md)
- [OPC工作流](docs/OPC-workflow.md)
- [Agent Teams](docs/agent-teams.md)
- [Smoke Test](docs/smoke-test.md)
- [版本历史](docs/versions/)
- [发版前审查清单](docs/plans/2026-05-25-release-readiness-checklist.md)

## License

MIT
