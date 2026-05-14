<div align="center">

# Humanize PPT

## 基于 AST 理论的人感 PPT 大纲导演 Skill

**先把资料变成人愿意听的大纲，再交给合适的PPT/HTML PPT Skill做风格探索、页面生成、演讲模式和部署上线**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://learnprompt.github.io/humanize-ppt/)
[![Release](https://img.shields.io/github/v/release/LearnPrompt/humanize-ppt?style=flat-square)](https://github.com/LearnPrompt/humanize-ppt/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[在线 Demo](https://learnprompt.github.io/humanize-ppt/) · [English](README.en.md) · [AST 理论](docs/AST-theory.md) · [OPC 工作流](docs/OPC-workflow.md) · [WorkBuddy Team Agent](docs/workbuddy-team-agent.md)

</div>

---

## 这是什么

Humanize PPT 是一个 **PPT 大纲导演 Skill**，不是又一个HTML PPT模板库，也不是普通的文本润色工具，更不是固定绑定4个下游Skill的Agent。

用 AST 理论把原始资料拆成：

- 观众是谁；
- 观众看之前是什么状态；
- 看完以后应该变成什么状态；
- 中间最大的认知张力是什么；
- 每一页如何推动状态转移；

然后再把这份干净的生产说明书交给合适的下游Skill生成HTML PPT、视频、演讲模式或部署包。我们会推荐op7418/guizang-ppt-skill、zarazhangrui/frontend-slides、heygen-com/hyperframes、lewislulu/html-ppt-skill这类HTML PPT相关Skill，但Humanize PPT本身不局限于这几个Skill。

## 核心判断

> **PPT 不只是信息容器，而是观众状态改变器。**

AI 直接生成 PPT 时，容易出问题的地方已经不是页面不够漂亮了，模型把自己的解释过程、中间推理痕迹和结构噪音都写进了页面里。

Humanize PPT 的作用是先把资料“洗干净”，重组成一条适合讲解、适合演示、适合下游生成的观众路径。

## WorkBuddy Team Agent 打包方向

Humanize PPT 在本仓库里仍然是Skill。面向腾讯 WorkBuddy 时，正确形态是：

```text
WorkBuddy Team Agent 专家团
├── 主理人 Agent：接收任务、建队、调度成员、汇总交付
├── 大纲导演 Agent：加载 humanize-ppt Skill，产出 AST 大纲和生产契约
├── 页面生成 Agent：加载用户选择或团队推荐的 PPT/HTML PPT Skill
├── 演讲增强 Agent：在定稿后补 presenter mode / speaker notes
└── QA Agent：检查内容、人感、路径、素材和交付可用性
```

也就是说：**把能力做成WorkBuddy里的Team Agent，但Humanize PPT本身还是一个可复用Skill。**

详见：[WorkBuddy Team Agent 打包方案](docs/workbuddy-team-agent.md)

## V0.1 能做什么

V0.1 先验证一个最小闭环：

```text
原始资料
→ 生成大纲：Humanize PPT / AST Outline Director Skill
→ 风格探索：frontend-slides和guizang-ppt-skill等下游Skill
→ 演讲模式：lewislulu/html-ppt-skill或Presenter Adapter
→ 静态上线：frontend-slides或其他部署适配器
```

当前包含：

- `SKILL.md`：Agent Skill 入口；
- `docs/AST-theory.md`：AST 理论；
- `docs/OPC-workflow.md`：Outline / Produce / Complete 工作流；
- `docs/workbuddy-team-agent.md`：腾讯 WorkBuddy Team Agent 打包方案；
- `contracts/`：输出契约模板；
- `scripts/humanize_ppt_v1.py`：本地最小 Demo Runner；
- `examples/`：脱敏测试素材。

## 快速开始

```bash
git clone https://github.com/LearnPrompt/humanize-ppt.git
cd humanize-ppt

python3 scripts/humanize_ppt_v1.py   --source examples/01-ai-tool-update/source.md   --out .humanize-ppt-runs/ai-tool-update   --title "AI 工具更新，不只是功能清单"

open .humanize-ppt-runs/ai-tool-update/styles/index.html
open .humanize-ppt-runs/ai-tool-update/presenter/index.html
```

也可以跑 Hermes 安装讲解案例：

```bash
python3 scripts/humanize_ppt_v1.py   --source examples/02-hermes-install-guide/source.md   --out .humanize-ppt-runs/hermes-install   --title "把 Hermes 装成一个真正能干活的 Agent"
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
  styles/
    index.html
    guizang-stable.html
    zara-editorial.html
    zara-contrast.html
  presenter/
    index.html
    notes.json
  deploy/
    index.html
    presenter.html
```

## 在线 Demo

- 首页：https://learnprompt.github.io/humanize-ppt/
- AI 工具更新风格探索：https://learnprompt.github.io/humanize-ppt/demo/styles/index.html
- AI 工具更新演讲模式：https://learnprompt.github.io/humanize-ppt/demo/presenter/index.html
- Hermes 安装讲解风格探索：https://learnprompt.github.io/humanize-ppt/demo/hermes-install/styles/index.html
- Hermes 安装讲解演讲模式：https://learnprompt.github.io/humanize-ppt/demo/hermes-install/presenter/index.html

## License

MIT
