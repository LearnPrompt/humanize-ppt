<div align="center">

# Humanize PPT

## 面向 Agent 的 PPT 工作流导演

**先把资料变成人愿意听的 AST 大纲，再交给下游 PPT Skill 做风格探索、页面生成、演讲模式和部署。**

[在线预览](https://learnprompt.github.io/humanize-ppt/) · [Release](https://github.com/LearnPrompt/humanize-ppt/releases) · [MIT License](LICENSE)

[English](README.en.md) · [AST理论](docs/AST-theory.md) · [OPC工作流](docs/OPC-workflow.md)

</div>

---

## 效果展示

Humanize PPT 不直接抢模板库的工作。它负责把资料整理成清晰的 AST 大纲，再把生产任务路由给适合的 PPT Skill。当前稳定样例包含中文 `guizang-ppt-skill` 路径和英文 `beautiful-html-templates / frontend-slides` 路径。

| 中文 guizang-ppt-skill 稳定样例 | English beautiful-html-templates / frontend-slides 样例 |
| --- | --- |
| [![中文 guizang 稳定样例](docs/showcase/hermes-agent-mastery/presenter/presenter-screenshot.png)](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/presenter/) | [![English Neo-Grid 样例](docs/showcase/hermes-agent-mastery/en/presenter/presenter-screenshot.png)](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/en/presenter/) |
| 打开[中文演讲模式](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/presenter/)或[中文 PPT](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/ppt/) | 打开[English presenter](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/en/presenter/)或[English deck](https://learnprompt.github.io/humanize-ppt/showcase/hermes-agent-mastery/en/ppt/) |

也可以查看已经发布的 [Skill 分享 PPT](https://learnprompt.github.io/humanize-ppt/showcase/skill-share/)。

## 30 秒开始：让 Agent 安装并使用

如果你正在使用 Codex、Claude Code、Hermes 或其他支持 Skill 的 Agent，把这段话发给它：

```text
请安装并使用 Humanize PPT Skill：
https://github.com/LearnPrompt/humanize-ppt

我要做一份 PPT。请先用 Humanize PPT 把资料整理成 AST 大纲，
再根据语言和场景选择下游 PPT Skill。
请确认 humanize-ppt、guizang-ppt-skill、beautiful-html-templates 和 frontend-slides 都可用。
中文内容优先走 guizang-ppt-skill 稳定成稿；
英文内容先用 beautiful-html-templates / frontend-slides 给我至少 5 个风格候选，等我选定后再生成完整 deck。
如果需要视频或动态素材，请确认 Remotion 相关能力可用。
最后请补 presenter / export / QA 修复与调优，并把输出路径告诉我。
```

如果你的 Agent 需要明确安装命令，可以让它执行：

```bash
npx skills add https://github.com/LearnPrompt/humanize-ppt.git -g -y
```

## 怎么跟 Agent 交流

你不需要一开始就写 CLI 参数。更自然的方式是按阶段给 Agent 下任务：

```text
我有一份关于「AI 工具更新」的资料，请用 Humanize PPT 先生成 PPT 大纲和风格预览。
目标观众是产品团队，重点不是功能清单，而是让他们理解这些工具会改变工作流。
```

```text
我选第 2 个风格。请继续生成完整 PPT，并补演讲模式。
如果需要素材，请先告诉我哪些页适合做 GPT 图片、SVG 图或 Remotion 短视频。
```

```text
请做 QA 修复/调优：检查标题是否重复、素材文字是否裁切、页面是否太空、视频是否能播放。
把问题列出来，能修的直接修，最后给我本地路径和可上线路径。
```

## CLI 复现方式

如果你想绕过 Agent、直接在本地复现，可以运行：

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

如果已经选中一个 Beautiful 模板，可以继续生成完整 deck，并补齐 presenter/export：

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out .humanize-ppt-runs/ai-tool-update-complete \
  --title "AI 工具更新，不只是功能清单" \
  --selected-template <slug> \
  --presenter-adapter \
  --export-adapter
```

## 能力

- **生成 AST 大纲**：把资料转成观众、状态转移、页面意图和讲述节奏。
- **路由下游 Skill**：根据语言和风格需求，把任务交给 guizang-ppt-skill、beautiful-html-templates、frontend-slides、presenter/export 等路径。
- **先预览再成稿**：英文路径默认先出至少 5 个风格候选，选中后再生成完整 deck。
- **补齐交付闭环**：生成 presenter、导出包、QA 修复/调优记录和可上线静态路径。

## 适合 / 不适合

适合：

- 你有资料、主题或大纲，但还缺一个可讲、可渲染、可 QA 调优的 PPT 大纲和成品路径。
- 你希望中文 PPT 默认走稳定 guizang-ppt-skill 成稿路径。
- 你希望英文 PPT 先做多风格探索，再选择一个方向继续生产。
- 你希望把资料交给 Agent 生成大纲、演讲模式和稳定复现的中英文 PPT 路径。

不适合：

- 你只想找一个单页模板库。
- 你希望它直接替代所有 HTML PPT / Remotion / 图片生成 Skill。
- 你还没有明确主题、观众或交付场景。

## 工作流路径

中文默认路径已经固定为：`Humanize PPT → guizang-ppt-skill → material QA 修复/调优 → presenter → static deploy`。当内容是中文且没有显式要求多风格探索时，优先把 guizang-ppt-skill 当作稳定成稿路径；成稿后再补素材 QA 调优、演讲模式和部署包。

英文默认路径已经固定为：`Humanize PPT → beautiful-html-templates / frontend-slides → style selection → full deck → presenter/deploy`。英文路径不直接跳到单一成稿风格；先基于主题生成至少 5 个可见候选，选中后再走完整 deck、演讲模式和部署。

Humanize PPT 当前重点是稳定“资料 → AST 大纲 → 风格预览/完整 deck → presenter/export → QA 修复/调优”的工作流。视频或动态素材可以作为页面材料进入流程；需要时请让 Agent 先确认 Remotion 相关能力已经安装并可运行。

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

根据是否选择模板、是否启用 presenter/export，部分输出目录可能为空或标记为待处理。

## 当前能力边界

- 推荐入口：`scripts/humanize_ppt.py`
- 历史版本说明：`docs/versions/`
- 版本计划与审查：`docs/plans/`
- 脱敏样例：`examples/`

## Reference

Humanize PPT 的设计参考了这些项目和操作规章：

- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)：中文稳定成稿、Swiss 风格约束、素材 QA。
- [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)：英文路径的多风格候选和 selected-template full deck。
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides)：英文 slide workflow、viewport-safe HTML deck、PPTX/发布方向。
- [huggingface/smolagents](https://github.com/huggingface/smolagents)：code-first Agent 工作流参考，帮助定义“Agent 读契约、执行工具、写回结果”的协作方式。
- [AST 理论](docs/AST-theory.md)、[OPC 工作流](docs/OPC-workflow.md)：Humanize PPT 自己的大纲方法、路由规则和执行边界。
- [Guizang material QA](references/guizang-material-qa.md)、[Guizang presenter deploy](references/guizang-presenter-deploy.md)、[English style gallery](docs/versions/v0.6.3-english-style-gallery.md)：当前中文和英文稳定路径的操作规章。

## License

MIT
