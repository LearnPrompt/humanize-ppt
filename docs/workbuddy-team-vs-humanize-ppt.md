# WorkBuddy Team vs Humanize PPT

> 回答 issue #1：「和 WorkBuddy 中 team 孰强孰弱？是模仿还是超越？」

结论：这不是“谁抄谁”或“谁一定更强”的问题。**Humanize PPT 是演讲生产内核；WorkBuddy Team 是多 Agent 分工与分发形态。**二者放在一起时，最好的关系是：Humanize PPT 提供 AST 大纲、媒体决策、生产契约和演讲体检；WorkBuddy Team 把这些能力拆成可调度的专家团队。

## 一句话定位

- **Humanize PPT**：把原始资料变成一场能讲的演讲。它关心观众状态转移、逐页意图、媒体槽、渲染后体检，以及哪一页“只能看不能讲”。
- **WorkBuddy Team**：把一个复杂任务拆给多个 Agent。它关心团队入口、角色分工、技能组合、规则约束、任务状态和可安装交付。

因此，Humanize PPT 不应该被描述成“一个 WorkBuddy team 的复刻”。更准确的说法是：

```text
Humanize PPT = PPT 演讲生产的方法论和质量内核
WorkBuddy Team = 把这个内核包装成多 Agent 工作台的产品形态
```

## 能力对比

| 维度 | Humanize PPT | WorkBuddy Team |
|---|---|---|
| 核心问题 | 怎么让 PPT 能讲、能交付 | 怎么让多个 Agent 协同做事 |
| 输入 | 原始材料、旧 PPT、链接、文档、转录、笔记 | 用户任务和 team 内部规则 |
| 中间产物 | `deck_brief.md`、`ast_outline.md`、`slide_plan.json`、`speaker_intent.md`、`asset_manifest.md`、production prompt | agent roles、skills、rules、任务编排、插件包 |
| 输出 | 下游渲染 brief、presenter shell、演讲体检报告、fix prompt | 可安装 team、可复用工作流 |
| 强项 | 观众状态转移、内容密度、演讲稿、渲染后 QA | 多角色协作、产品化入口、分发和复用 |
| 风险 | 如果被误解成 renderer，会和模板库职责混淆 | 如果只包装角色，没有 AST/QA 内核，会变成“技能列表展示” |

## 最佳组合形态

WorkBuddy 里的 `humanize-ppt-team` 应该是一支“PPT 制片团队”，而不是一个更大的单体 PPT 生成器：

```text
@humanize-ppt-team-lead
  负责拆阶段、守 AST、写 router_plan/run_manifest、最终验收

@outline-director
  使用 humanize-ppt，把原始材料变成 AST 大纲和 slide_plan

@guizang-renderer / @frontend-slides-renderer
  按 Humanize production prompt 原生渲染，不改 Humanize 中间产物

@video-motion-agent
  按 video_slots.json 生产 Remotion / HyperFrames 素材

@html-ppt-presenter
  生成演讲模式、notes、timer、next slide 视图

@qa
  跑 Humanize --qa-from，输出 qa_report.md / fix_prompt.md
```

这时 WorkBuddy Team 的“强”来自可调度、可安装、可复用；Humanize PPT 的“强”来自每个 agent 都围绕同一份演讲契约工作，而不是各自发挥。

## 判断标准

如果问题是下面这些，用 Humanize PPT 作为内核更重要：

- 原始材料很散，想变成一场能讲的演讲；
- PPT 看起来漂亮但讲不下去；
- 需要逐页决定图、SVG、视频、截图；
- 需要渲染后自动检查哪几页翻车；
- 需要让下游 guizang/frontend-slides/beautiful 原生渲染，但不要让它们吞原始材料。

如果问题是下面这些，用 WorkBuddy Team 形态更重要：

- 要把流程发布给别人安装；
- 要让多个 Agent 分工执行；
- 要在 WorkBuddy/CodeBuddy 里有清晰入口；
- 要把 rules、skills、agents 打包成插件；
- 要让用户不理解 CLI 也能跑完整流程。

## 对外说法

推荐：

> Humanize PPT 不是单个模板渲染器，也不是简单模仿 WorkBuddy Team。它是 PPT 演讲生产的内核：先用 AST 把内容变成能讲的线，再把媒体、渲染、演讲模式、QA 拆给下游专家。WorkBuddy Team 是把这套内核产品化成可安装 AI 团队的外壳。

避免：

- “Humanize PPT 比 WorkBuddy Team 更强。”
- “Humanize PPT 是 WorkBuddy Team 的替代品。”
- “WorkBuddy Team 只是套壳。”

更准确的是：**Humanize PPT 解决 PPT 这类任务的专业深度，WorkBuddy Team 解决多 Agent 产品化的组织形态。**
