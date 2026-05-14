# Humanize PPT × WorkBuddy Team Agent 打包方案

## 结论

Humanize PPT 在本仓库中的身份保持不变：它是一个 **PPT 大纲导演 Skill**。

面向腾讯 WorkBuddy 时，不是把 Humanize PPT 改名成 Agent，也不是把工作流硬绑定到4个Skill；正确做法是：

```text
把 Humanize PPT Skill 放进 WorkBuddy Team Agent 专家团，
再把“大纲、页面、视频、演讲、质检”等职责拆成多个 Agent。
```

Humanize PPT 负责产出适配下游Skill的结构化大纲和生产契约；Team Agent 负责建队、调度、传递上下文、综合产物和交付。

---

## 1. 从 WorkBuddy 规范提取的关键约束

根据《WorkBuddy 专家开发规范 v2.1》：

1. 专家类型有两种：`agent` 和 `team`。我们这里应该做 `team`。
2. Team 型专家必须包含：
   - `.workbuddy-plugin/plugin.json`
   - `agents/`
   - `avatars/`
   - `settings.json`
3. `agents/`、`skills/`、`bin/` 必须在插件根目录，不能放进 `.workbuddy-plugin/`。
4. 专家包不使用 `hooks/`、`commands/`、`.lsp.json`。
5. 主理人文件名不能叫通用 `team-lead.md`，必须带专家团前缀，例如 `humanize-ppt-team-lead.md`。
6. `settings.json.agent` 必须等于 `plugin.json.agentName`，也必须等于主理人 MD frontmatter 中的 `name`。
7. Agent MD frontmatter 不能声明 `tools` 字段，工具权限由系统统一分配。
8. 主理人必须写入“团队协作机制（铁律）”：建立团队、调度成员、消息中转、成员结论为准，禁止主理人模拟成员产出。
9. Skill 是可选资源，但非常适合放 Humanize PPT 这种可复用能力。

---

## 2. 推荐包结构

```text
humanize-ppt-team/
├── .workbuddy-plugin/
│   └── plugin.json
├── avatars/
│   ├── team.png
│   ├── humanize-ppt-team-lead.png
│   ├── outline-director.png
│   ├── renderer.png
│   ├── presenter.png
│   └── qa.png
├── agents/
│   ├── humanize-ppt-team-lead.md
│   ├── outline-director.md
│   ├── renderer.md
│   ├── presenter.md
│   └── qa.md
├── skills/
│   └── humanize-ppt/
│       ├── SKILL.md
│       ├── contracts/
│       ├── docs/
│       ├── adapters/
│       ├── examples/
│       └── scripts/
├── settings.json
└── README.md
```

注意：这里的 `skills/humanize-ppt/` 是把当前仓库作为Skill资源装入专家团包；不是把 Humanize PPT 改成 Agent。

---

## 3. Agent 分工

## 3.1 主理人 Agent：humanize-ppt-team-lead

职责：

1. 接收用户任务，判断目标形式：视频、图文、短图文、路演PPT、培训课件、产品发布等。
2. 创建本次协作团队。
3. 将原始资料交给大纲导演 Agent。
4. 根据大纲导演产出的契约选择后续成员：页面生成、视频、演讲、质检。
5. 汇总成员结果，输出最终交付物和下一步建议。

主理人不直接写大纲、不直接生成页面、不假装成员已经工作。

## 3.2 大纲导演 Agent：outline-director

加载：

```text
humanize-ppt
```

职责：

1. 读取原始资料。
2. 用 AST 理论产出观众状态转移路径。
3. 输出标准契约：
   - `deck_brief.md`
   - `ast_outline.md`
   - `slide_plan.json`
   - `speaker_intent.md`
   - `asset_manifest.md`
   - `video_slots.json`
4. 根据目标形式，给下游Skill写清楚生产说明。

## 3.3 页面生成 Agent：renderer

加载：

```text
用户指定的 PPT / HTML PPT Skill
或团队推荐的 guizang / frontend-slides / html-ppt 等 Skill
```

职责：

1. 只消费大纲导演输出的契约，不直接吃原始资料。
2. 按用户目标选择合适渲染路径。
3. 产出 HTML PPT、页面文件、可预览版本或部署包。

推荐但不绑定的路径：

- `guizang-ppt-skill`：中文稳定成稿。
- `frontend-slides` / Zara 风格能力：风格探索、页面生成、上线。
- 其他HTML PPT Skill：只要能消费 Humanize PPT 的契约，都可以接入。

## 3.4 Presenter Agent：presenter

职责：

1. 在PPT已经定稿后增加演讲模式。
2. 处理当前页/下一页、speaker notes、计时器、演讲控制。
3. 不把演讲模式当作一种视觉风格。

## 3.5 QA Agent：qa

职责：

1. 检查 AST 是否被保留。
2. 检查页面是否塞入模型推理噪音。
3. 检查标题、转场、中文表达是否自然。
4. 检查图片、视频、链接、部署路径是否可用。
5. 输出 `qa_report.md` 和修复建议。

---

## 4. plugin.json 草案

```json
{
  "name": "humanize-ppt-team",
  "version": "0.1.0",
  "description": "A WorkBuddy Team Agent that turns raw material into human-centered presentation outlines and coordinates compatible PPT/HTML PPT skills for production",
  "author": {
    "name": "LearnPrompt",
    "email": "team@example.com"
  },
  "agents": [
    "./agents/humanize-ppt-team-lead.md",
    "./agents/outline-director.md",
    "./agents/renderer.md",
    "./agents/presenter.md",
    "./agents/qa.md"
  ],
  "skills": [
    "./skills/humanize-ppt"
  ],
  "expertType": "team",
  "agentName": "humanize-ppt-team-lead",
  "teamInfo": {
    "leadAgent": "humanize-ppt-team-lead",
    "memberAgents": ["outline-director", "renderer", "presenter", "qa"]
  },
  "displayName": {
    "en": "Humanize PPT Team",
    "zh": "人感PPT专家团"
  },
  "profession": {
    "en": "Presentation Planning and Production Team",
    "zh": "PPT大纲与生成协作专家团"
  },
  "displayDescription": {
    "en": "Turns raw material into audience-aware presentation briefs, then coordinates compatible PPT/HTML PPT skills for rendering, presenter mode, and delivery QA.",
    "zh": "先用AST把原始资料变成人愿意听的大纲，再调度合适的PPT/HTML PPT Skill完成页面生成、演讲模式和交付质检。"
  },
  "avatar": "avatars/team.png",
  "categoryId": "01-ProductDesign",
  "defaultInitPrompt": {
    "zh": "帮我把这份资料做成人感PPT大纲，并选择合适的HTML PPT生成路径",
    "en": "Turn this material into a human-centered presentation outline and choose a suitable HTML PPT production path"
  },
  "plugin": "humanize-ppt-team",
  "tags": [
    { "en": "Presentation", "zh": "PPT" },
    { "en": "Outline", "zh": "大纲导演" },
    { "en": "HTML Slides", "zh": "HTML PPT" },
    { "en": "Team Agent", "zh": "专家团" }
  ],
  "quickPrompts": [
    { "en": "Create a deck outline", "zh": "把资料整理成人感PPT大纲" },
    { "en": "Choose a slide production path", "zh": "帮我选择合适的HTML PPT生成路径" },
    { "en": "Review my deck narrative", "zh": "检查这份PPT的人感和讲述路径" }
  ],
  "members": [
    { "id": "humanize-ppt-team-lead", "name": {"en":"Lead","zh":"主理人"}, "profession": {"en":"Team Lead & Orchestrator","zh":"主理人与调度官"}, "avatar": "avatars/humanize-ppt-team-lead.png", "role": "lead" },
    { "id": "outline-director", "name": {"en":"Aster","zh":"大纲导演"}, "profession": {"en":"AST Outline Director","zh":"AST大纲导演"}, "avatar": "avatars/outline-director.png", "role": "member" },
    { "id": "renderer", "name": {"en":"Rhea","zh":"页面生成师"}, "profession": {"en":"PPT/HTML PPT Renderer","zh":"PPT/HTML PPT生成师"}, "avatar": "avatars/renderer.png", "role": "member" },
    { "id": "presenter", "name": {"en":"Noah","zh":"演讲增强师"}, "profession": {"en":"Presenter Mode Specialist","zh":"演讲模式专家"}, "avatar": "avatars/presenter.png", "role": "member" },
    { "id": "qa", "name": {"en":"Quinn","zh":"质检官"}, "profession": {"en":"Narrative and Delivery QA","zh":"内容与交付质检"}, "avatar": "avatars/qa.png", "role": "member" }
  ]
}
```

---

## 5. 主理人 Prompt 必须强调的边界

主理人 MD 中必须写清楚：

1. Humanize PPT 是Skill，不是主理人自己。
2. 主理人负责 WorkBuddy Team Agent 的团队流程。
3. 大纲产出必须由 `outline-director` 调用 Humanize PPT Skill 完成。
4. 页面生成 Agent 可以适配不同Skill，不限于 guizang、Zara、HyperFrames、Presenter。
5. 这几个HTML PPT Skill可以作为推荐路径展示给用户，但不能写死为唯一能力。
6. 所有成员产出必须真实来自对应成员，不允许主理人代写。

---

## 6. 推荐传播表达

更准确的一句话：

> Humanize PPT 是一个人感PPT大纲导演Skill。放进腾讯 WorkBuddy 后，它可以作为专家团里的大纲能力，由主理人Agent调度页面生成、视频、演讲模式和质检Agent，把任意资料变成更像人讲、更适合交付的PPT生产流程。

短版：

> Humanize PPT 不直接抢下游PPT Skill的活，它先把资料变成人愿意听的大纲，再让 WorkBuddy Team Agent 调度合适的Skill把它做出来。
