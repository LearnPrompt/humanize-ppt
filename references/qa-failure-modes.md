# 演讲体检失败模式目录（v0.8.0）

演讲体检（即此前的 QA 循环，CLI 仍是 `--qa-from`）是 Humanize PPT 在签收前对渲染后 HTML 做的逐页核对。体检对的不是美观，是大纲：逐页核对渲染结果和大纲页的差异，把「只能看、不能讲」的页揪出来，直到每一页都拿得出口去讲。

先用完整的句子说清楚什么叫失败的页。一页只有几个字，没把这页该说的意思说完；或者这页没有完成它承诺的观众状态转移，听众看完这页，状态没有从 A 到 B。这样的页不应该存在。演讲体检就是把它揪出来，并生成修复指令（`fix_prompt.md`）让下游 skill 重渲。

本文件是体检扫描的失败模式人读目录。代码侧的唯一事实来源是 `scripts/humanize_ppt_v2.py` 里的 `FAILURE_MODES` 字典，两边按 id 一一对应。

**目录纪律：只列代码里真实存在的规则。** 不写愿望清单，不发明检查。某类失败真实存在但脚本还测不出来的，会写进[静态扫描还测不出的失败类](#静态扫描还测不出的失败类)，不会被包装成模式。

## 范围

失败模式分两层：

- **第一层：渲染器无关的失败类。** 症状在任何渲染器的产物上都可能出现。v0.8.0 起，`placeholder-residue` 这条规则本身也是渲染器无关的（scope 为 `any`），对任何下游渲染的 HTML 都会跑。
- **第二层：渲染器专属模式。** 按渲染器 id 划定范围：
  - **guizang**：Style A 和 Style B 都适用，特别注明的除外
  - **guizang-style-a**：仅 Style A
  - **guizang-style-b**：仅 Style B（Swiss 锁定）
  - **frontend-slides**：暂无专属规则（原因见下文英文渲染器小节）
  - **beautiful-html-templates**：暂无专属规则（原因见下文英文渲染器小节）

## 第一层：渲染器无关的失败类

下表是体检今天覆盖的失败类，以及实现它们的具体规则。

| 失败类 | 观众视角会看到什么 | 已实现的规则 |
| --- | --- | --- |
| 模板占位残留 | 正式页面上出现 `[必填]`、`SLIDES_HERE`、lorem ipsum、TODO、TBD 这样的半成品字样 | `placeholder-residue`（scope `any`，对所有渲染器生效） |
| 动画降级 | 整个 deck 一动不动，讲述节奏塌掉 | `low-power-default`、`data-anim-thin` |
| 布局契约违约 | 页数或布局和大纲对不上，有的页该有的内容没出现 | `swiss-sxx-count-mismatch`、`swiss-sxx-invented-id`、`swiss-low-diversity` |
| 背景层缺失 | Hero 页背景一片空白，页面像没做完 | `webgl-canvas-missing` |
| AI 草稿残留 | 页面上出现「作为AI」「首先我需要」这类模型脚手架文字 | brief 模式检查 `visible_slide_text_has_no_ai_draft_markers`（`write_qa` 里的 `BANNED_VISIBLE_PATTERNS`），在渲染之前就跑在 slide plan 上 |

### 静态扫描还测不出的失败类

文字溢出、对比度过低、字重降级、视口截断、图文错位、徽章或装饰元素遮挡正文，这些都是真实的渲染失败类，但它们需要真实浏览器渲染才能检测，`scripts/humanize_ppt_v2.py` 的静态扫描今天测不出来。按目录纪律，它们不被列为模式。在 Humanize 有真实检测手段之前，这些靠下游的视觉检查清单（`references/guizang-material-qa.md`）和人工截图复核兜底。

真实案例：2026-06-13 英文 deck（`docs/showcase/hermes-agent-mastery/en/ppt/`）的体检中，静态扫描通过，而截图逐页复核发现页码徽章遮挡 9 页正文，观众会看到「uires confirmation.」这样的断句。修复与复检记录见 `docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md`。截图复核是体检方法论的一半，今天还没自动化。

还有一类失败，连「页本身」都是对的，错的是**怎么截它**——

**WebGL hero 封面静态截图捕获不到 → 封面空白。** Guizang Style A 的封面用 WebGL hero canvas 画背景。HTML 完全正确（`canvas#bg-dark`/`canvas#bg-light` 都在、`data-anim` 充足、`low-power` 没激活，所有静态检查全过），但对它截的那张 PNG 是空白的——因为 canvas 在页面加载后才异步绘制首帧，截图发生在绘制之前，截到的是还没上色的画布。`webgl-canvas-missing` 这类静态规则查的是「画布在不在 HTML 里」，查不出「画布画出来没、截图截到没」。这是一个**正确的页 + 错误的截图 = 空白产物**的失败类，和文字溢出那种「页本身有问题」的失败类不同，但同样要靠真实渲染/截图复核才能发现。

实证：2026-06 的 9 风格 agent 封面试验里，Style A `ink-classic` 封面的静态截图只有 14KB，肉眼看是一张空白页（同批 Style B 瑞士静态封面截图正常）。这批截图因此撤回不入库（宁空不摆拍）。

兜底规则（写进了 v0.9 风格画廊的封面渲染命令，见 `references/style-gallery-spec.md`）：截 WebGL hero 页时，以活页 `cover.html` 为准、`cover.png` 仅作缩略；截图前等 canvas 完成首帧（延迟 ≥1.5s）；`cover.png` 小于 20KB 一律判为截图失败而非空封面，重截或只交活页。这条今天还测不出来（Humanize 不读 PNG 字节），所以列在这里，不包装成 `FAILURE_MODES` 模式。

## 模式目录

每条模式给四样东西：症状、观众视角会看到什么、检测方式（`scripts/humanize_ppt_v2.py` 里的规则函数名）、修复指令方向（`fix_prompt.md` 会让下游 skill 做什么）。

### `placeholder-residue`（所有渲染器）

**症状：** 模板占位符泄漏进了渲染后的 HTML。下游 skill 自己的替换流程没有跑完，或者填充内容时留下了占位文本。v0.8.0 起此规则渲染器无关。

**观众视角会看到什么：** 正式页面上出现 `[必填]`、`<!-- SLIDES_HERE -->`、lorem ipsum、TODO、TBD 这样的字样。观众立刻知道这页没做完。

**检测：** `check_placeholder_residue`。渲染 HTML 里出现 `[必填]` 或 `SLIDES_HERE` 即 fail；出现 lorem ipsum（不区分大小写）、独立单词 TODO 或 TBD 也 fail。

**修复指令方向：** 替换所有 `[必填]` 占位符，删掉 `<!-- SLIDES_HERE -->` 标记，把 lorem / TODO / TBD 填充文本换成成品内容；下游 skill 自己的替换流程必须完整跑一遍。

### `low-power-default`（guizang）

**症状：** 渲染后的 HTML 里 `body.low-power` 处于激活状态。它会压制动画，本意是运行时手动开启的省电选项，不该是默认值。

**观众视角会看到什么：** deck 打开就是全静态的，本该有的入场动画和节奏全部消失。

**检测：** `check_low_power_default`。`<body>` 的 class 列表里含 `low-power` 即 fail。

**修复指令方向：** 把 `low-power` 从 body class 里去掉，动画必须在首次加载时就播放。

### `webgl-canvas-missing`（guizang-style-a）

**症状：** 双 WebGL 画布（`canvas#bg-dark` 和 `canvas#bg-light`）缺失或只有一半。没有它们，Hero 背景渲染不出来。

**观众视角会看到什么：** Hero 页背景一片空白或一块死色，开场页像半成品。

**检测：** `check_webgl_canvas_missing`。`canvas#bg-dark` 和 `canvas#bg-light` 两个都在才算过。

**修复指令方向：** 把两块画布都加回去，让 Style A 的 WebGL Hero 背景能渲染。

### `data-anim-thin`（guizang-style-a）

**症状：** `data-anim` / `data-animate` 标记太少，撑不起一份能看的 deck。已验证的 Ink Classic 基准里有 86 处。

**观众视角会看到什么：** 翻页之间几乎没有任何元素入场动画，整份 deck 像一摞静态海报。

**检测：** `check_data_anim_thin`。少于 3 个硬性 fail，少于 10 个软性 warn。

**修复指令方向：** 在非封面页补充 `data-anim` / `data-animate` 标记，目标 10 个以上（Ink Classic 是 86 个）。

### `swiss-sxx-count-mismatch`（guizang-style-b）

**症状：** 渲染 HTML 里 `data-layout="Sxx"` 标记的数量和 `slide_plan.json` 的页数对不上。

**观众视角会看到什么：** 有的大纲页根本没渲染出来，或者多出了大纲里没有的页；讲到那页时投影上没有对应内容。

**检测：** `check_swiss_sxx_count_mismatch`。Sxx 数量不等于页数即 fail。

**修复指令方向：** 让 `data-layout="Sxx"` 标记数量等于 `slide_plan.json` 的页数，由下游 skill 重新产出。

### `swiss-sxx-invented-id`（guizang-style-b）

**症状：** 某个 `data-layout="Sxx"` 的值不在注册集（`S01` 到 `S22`）里。下游 skill 没有从 `references/layouts-swiss.md` 的注册集里选，而是自己编了一个布局 ID。

**观众视角会看到什么：** 那一页的版式不在 Swiss 体系里，和全 deck 的视觉语言脱节，观众能感觉到这页「画风不对」。

**检测：** `check_swiss_sxx_invented_id`。任何 Sxx 值不属于 S01 到 S22 即 fail。

**修复指令方向：** 把自编的 Sxx 值换成 S01 到 S22 里的注册布局 ID。

### `swiss-low-diversity`（guizang-style-b，软性警告）

**症状：** 8 页的 deck 里不到 6 种不同的 `Sxx` 值（其他长度按页数的 60% 向上取整算下限）。整份 deck 读起来像同一个版式盖了 n 遍章。

**观众视角会看到什么：** 每一页长得几乎一样，翻了三页之后观众开始走神，因为版面没有给出任何「这页和上页不同」的信号。

**检测：** `check_swiss_low_diversity`。不到 3 种硬性 fail，低于 60% 下限软性 warn。

**修复指令方向：** 让 Swiss 布局多样化，尽量每页换一个注册 Sxx，下限是 60% 的不重复率。

## 英文渲染器：专属规则为什么还空着

v0.8.0 实测状态（对应 `registry/renderer_registry.json`）：

- `beautiful-html-templates` 标为 `"support_level": "brief+qa-verified"`：brief 出口可用，且 2026-06-13 在它的真实 Neo-Grid deck 上完整跑通了演讲体检（扫描、发现、修复、复检，逐轮记录见 `docs/showcase/hermes-agent-mastery/en/qa/presentation-checkup-2026-06-13.md`）。但 `FAILURE_MODES` 里仍然没有 beautiful 专属规则，目前对它生效的只有渲染器无关层的 `placeholder-residue`，所以不标 `full`。
- `frontend-slides` 标为 `"support_level": "brief-only"`：brief 出口可用（production prompt 正常产出、可消费），但体检还没在任何一份 frontend-slides 的真实渲染产物上跑过，也没有它的专属规则。

专属规则小节会一直空着，直到对应渲染器的真实产物在体检里跑出可验证的发现。宁空不摆拍，和 README showcase 同一条班规。

## 体检怎么用这份目录

1. `run_checks(html, plan, modes)` 跑每条模式的检查函数，返回发现列表：`[{id, severity, pages, evidence}]`。
2. `_write_qa_report` 产出人读的 `qa_report.md`。
3. `_write_fix_prompt` 产出下游 skill 可执行的 `fix_prompt.md`（比如「把 S04 的 `data-layout="S99"` 换成注册的 Sxx 布局」）。
4. 迭代跟踪器 `qa_iteration.json` 记录轮次、上一轮哪些发现已解决、哪些还开着。

体检上限是 `--max-qa-iterations`（默认 3）。到达上限仍有未解决发现时，`qa_status` 变为 `needs-human`，交回给下一个 Agent 或人来决定。
