# Humanize PPT 目录简化 + SuperPower / Office Hours 前置计划

> **For Hermes:** 当前阶段只做计划与审批，不直接改业务代码。后续执行时按小步提交，每一步都先验证再进入下一步。

**日期：** 2026-05-22  
**仓库：** `/Users/carl/Downloads/humanize-ppt`  
**远端：** `git@github.com:LearnPrompt/humanize-ppt.git`  
**当前分支：** `main`  
**当前版本状态：** `SKILL.md` 已到 `0.5.0`，主入口是 `scripts/humanize_ppt_v5.py`，但核心实现仍集中在 `scripts/humanize_ppt_v2.py`。

---

## 0. 结论

这次不建议先继续叠新版本。推荐先做一次“减熵版整理”：

1. **先简化代码目录和入口命名**：让外部用户知道应该跑哪个脚本、看哪份文档、忽略哪些历史材料。
2. **再用 SuperPower 做下一版设计**：把 V0.6 或 V1.0 的范围写成可审查 spec。
3. **再用 Office Hours 做价值审查**：确认最窄切口、真实用户场景、哪些功能暂缓。
4. **最后再决定是否发新版本**：只有目录、入口、README、demo、测试都清爽后，再更新版本号和 release note。

一句话：**先整理地基，再讨论方向，最后发版本。**

---

## 1. 当前仓库观察

### 1.1 文件结构现状

当前 tracked 文件主要集中在：

- `scripts/`：5 个脚本入口。
- `docs/`：理论文档、版本说明、demo、showcase、历史计划。
- `contracts/`：输出契约模板和 schema。
- `registry/`：renderer 能力注册表。
- `references/`：公开传播、适配器和打包经验。
- `tests/`：目前只有 `tests/test_beautiful_preview.py` 一组测试。

### 1.2 代码复杂度信号

当前脚本行数：

- `scripts/humanize_ppt_v1.py`：123 行。
- `scripts/humanize_ppt_v2.py`：1259 行。
- `scripts/humanize_ppt_v3.py`：12 行。
- `scripts/humanize_ppt_v4.py`：12 行。
- `scripts/humanize_ppt_v5.py`：12 行。

关键问题：

- V0.3 / V0.4 / V0.5 是 wrapper，核心逻辑都堆在 `humanize_ppt_v2.py`。
- README 已经面向 V0.5，但脚本命名仍保留多版本入口，外部用户会困惑。
- `docs/demo/`、`docs/showcase/`、`.humanize-ppt-runs/`、版本说明文档共同存在，容易分不清“公开入口”“历史材料”“生成产物”。
- 当前环境缺少 `pytest`，直接运行 `python -m pytest -q` 失败：`No module named pytest`。因此测试计划要先补安装说明或改为 stdlib 可跑的 smoke check。

---

## 2. 本轮目标与非目标

### 2.1 目标

本轮只做“简化目录 + 发版前置审查”，不做新功能。

交付物：

1. 一份目录瘦身方案。
2. 一份 SuperPower 设计审查问题清单。
3. 一份 Office Hours 价值审查问题清单。
4. 一份后续实施计划，明确每一步要改哪些文件、怎么验证、什么时候提交。

### 2.2 非目标

本轮不做：

- 不新增 V0.6 功能。
- 不重写 Humanize PPT 的 AST 理论。
- 不引入新的下游 renderer。
- 不做大规模架构重构。
- 不删除历史材料，只移动或归档，并保持可追溯。
- 不改 GitHub Pages 公开路径，除非后续单独确认。

---

## 3. 推荐目录目标形态

建议把仓库整理成“用户入口清楚、开发入口清楚、历史材料收纳”的结构：

```text
humanize-ppt/
  README.md
  README.en.md
  SKILL.md
  LICENSE

  scripts/
    humanize_ppt.py              # 推荐主入口，后续新增
    humanize_ppt_v1.py           # legacy，保留
    humanize_ppt_v2.py           # legacy/core，下一阶段再拆
    humanize_ppt_v3.py           # legacy wrapper
    humanize_ppt_v4.py           # legacy wrapper
    humanize_ppt_v5.py           # legacy wrapper

  contracts/
    *.schema.json
    *.template.md

  registry/
    renderer_registry.json

  examples/
    01-ai-tool-update/source.md
    02-hermes-install-guide/source.md

  tests/
    test_beautiful_preview.py

  docs/
    index.md
    AST-theory.md
    OPC-workflow.md
    router-rules.md
    presenter-adapter.md
    versions/
      v0.2-router-edition.md
      v0.3-preview-first.md
      v0.4-selected-template-full-deck.md
      v0.5-presenter-export-adapter.md
    plans/
      *.md
    demo/
      ...                        # 明确标注为 GitHub Pages demo
    showcase/
      ...                        # 明确标注为公开展示素材

  references/
    *.md
```

这一步先不强拆 `humanize_ppt_v2.py`，只解决“入口混乱”和“文档散落”。大拆模块放到下一轮。

---

## 4. SuperPower 设计审查问题

进入代码改动前，先用 SuperPower 把“目录简化”的设计边界固定下来。

建议只问 4 个问题：

1. **用户第一眼应该跑哪个命令？**  
   推荐答案：`python3 scripts/humanize_ppt.py ...`，旧版脚本作为 legacy wrapper 保留。

2. **公开文档优先服务谁？**  
   推荐答案：先服务“想试用 Humanize PPT 的内容创作者 / AI 工具玩家”，开发者文档放在 docs 深处。

3. **历史版本文档是否移动？**  
   推荐答案：移动到 `docs/versions/`，README 只保留当前稳定链路。

4. **是否现在拆 `humanize_ppt_v2.py`？**  
   推荐答案：不在本轮拆。先新增主入口和整理文档，再单独开“代码模块化”计划。

---

## 5. Office Hours 价值审查问题

目录整理完成后，再问这 6 个问题，决定要不要开新版本：

1. **谁现在真的痛？**  
   是想快速把资料变成可讲PPT的人，还是想探索多个HTML PPT Skill的人？

2. **他们现在不用 Humanize PPT 时怎么做？**  
   是直接丢给 PPT 生成器、手写大纲、还是让 Claude/Codex 生成 HTML？

3. **最窄可用切口是什么？**  
   推荐切口：`source.md → AST contract → 3 个真实风格预览 → 选 1 个生成完整HTML deck → presenter/export`。

4. **哪一步最能证明价值？**  
   推荐信号：用户看到 3 个预览后能马上选，并且最终 deck 没有明显 AI 味结构噪音。

5. **哪些功能只是显得高级？**  
   推荐暂缓：多 renderer 自动全链路真实调用、部署平台集成、视频生成、WorkBuddy 团队包自动上传。

6. **下一版应该叫 V0.6 还是 V1.0？**  
   推荐：如果只是目录简化 + 主入口，叫 V0.5.1 或 V0.6；只有跑通“单入口稳定交付链路”后再考虑 V1.0。

---

## 6. 实施计划

### Phase 1：基线保护

**目标：** 在改目录前确认当前仓库可回滚、当前公开入口可解释。

步骤：

1. 运行 `git status --short`，确认没有未提交改动。
2. 记录最近 5 个 commit：`git log --oneline -5`。
3. 记录 tracked 文件清单：`git ls-files`。
4. 尝试运行测试：`python -m pytest -q`。
5. 如果本机没有 pytest，记录为环境问题，不把它当作代码失败。

验收：

- 有清晰基线记录。
- 知道测试失败是因为缺依赖还是代码错误。

### Phase 2：新增稳定主入口

**目标：** 降低用户理解成本。

建议动作：

1. 新增 `scripts/humanize_ppt.py`。
2. 让它调用当前稳定入口 `humanize_ppt_v5.main()` 或直接调用 `humanize_ppt_v2.main()`。
3. 保留 `humanize_ppt_v1.py` 到 `humanize_ppt_v5.py`，但 README 只推荐 `humanize_ppt.py`。
4. 在旧 wrapper 顶部注释里标明 legacy / compatibility。

验收：

```bash
python3 scripts/humanize_ppt.py --help
python3 scripts/humanize_ppt_v5.py --help
```

两者都能正常输出帮助信息。

### Phase 3：整理文档目录

**目标：** 把“当前说明”和“历史说明”分开。

建议动作：

1. 新建 `docs/versions/`。
2. 移动：
   - `docs/v0.2-router-edition.md` → `docs/versions/v0.2-router-edition.md`
   - `docs/v0.3-preview-first.md` → `docs/versions/v0.3-preview-first.md`
   - `docs/v0.4-selected-template-full-deck.md` → `docs/versions/v0.4-selected-template-full-deck.md`
   - `docs/v0.5-presenter-export-adapter.md` → `docs/versions/v0.5-presenter-export-adapter.md`
3. 更新 README / SKILL.md 中对应路径。
4. 保留 `docs/plans/`，不混入正式版本文档。

验收：

```bash
grep -R "docs/v0\." -n README.md README.en.md SKILL.md docs || true
```

不应再出现旧路径引用。

### Phase 4：整理 README 的当前链路

**目标：** README 只讲当前推荐路径，不把历史版本全摊给用户。

建议动作：

1. 快速开始改成主入口：`python3 scripts/humanize_ppt.py ...`。
2. 保留一句：“旧版入口仍保留用于兼容”。
3. 把 V0.1-V0.4 的细节移到 `docs/versions/`。
4. 在线预览只保留稳定入口和 showcase，隐藏调试 demo 解释清楚。

验收：

- 用户 30 秒内能知道该跑哪条命令。
- README 不再像版本考古。

### Phase 5：补一个最小 smoke 验证

**目标：** 即使没有 pytest，也能验证主入口不坏。

建议动作：

1. 新增或记录一个 smoke 命令：

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out /tmp/humanize-ppt-smoke \
  --title "AI 工具更新，不只是功能清单" \
  --style-mode preview-first
```

2. 验证至少生成：
   - `deck_brief.md`
   - `ast_outline.md`
   - `slide_plan.json`
   - `router_plan.json`
   - `run_manifest.json`

验收：

```bash
test -f /tmp/humanize-ppt-smoke/deck_brief.md
test -f /tmp/humanize-ppt-smoke/slide_plan.json
test -f /tmp/humanize-ppt-smoke/run_manifest.json
```

### Phase 6：新版本决策

**目标：** 决定是否发版，以及版本号怎么定。

建议判断：

- 只做主入口 + 文档整理：`v0.5.1`。
- 主入口 + 文档整理 + smoke 验证文档 + 小规模测试修复：`v0.6.0`。
- 完成模块化拆分、稳定单入口完整交付链路后：再考虑 `v1.0.0`。

---

## 7. 建议任务拆分

### Task 1：提交计划文档

**文件：**

- Create: `docs/plans/2026-05-22-directory-simplification-superpower-office-hours-plan.md`

**验收：**

- 文档存在。
- 计划包含目标、非目标、目录目标形态、SuperPower 问题、Office Hours 问题、实施步骤。

### Task 2：新增主入口

**文件：**

- Create: `scripts/humanize_ppt.py`
- Modify: `README.md`
- Modify: `README.en.md`

**验收：**

- `python3 scripts/humanize_ppt.py --help` 可跑。
- README 首推新入口。

### Task 3：移动版本文档

**文件：**

- Move: `docs/v0.*.md` → `docs/versions/`
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `README.en.md`

**验收：**

- 没有旧路径残留。
- 链接不失效。

### Task 4：补 smoke 验证说明

**文件：**

- Modify: `README.md`
- Optional Create: `scripts/smoke_check.py` 或 `docs/smoke-test.md`

**验收：**

- 无 pytest 时也能验证主链路。
- 有 pytest 时继续跑 `python -m pytest -q`。

### Task 5：发版前审查

**文件：**

- Create: `docs/plans/2026-05-22-release-readiness-checklist.md` 或追加到当前计划。

**验收：**

- 明确版本号建议。
- 明确 release note 草稿。
- 明确暂缓功能。

---

## 8. 风险与处理

| 风险 | 处理 |
|---|---|
| 移动 docs 后 GitHub Pages 链接失效 | 只移动内部版本说明，不动 `docs/index.html`、`docs/demo/`、`docs/showcase/` 公开入口 |
| 用户仍然看到 v1-v5 多入口困惑 | README 只推荐 `scripts/humanize_ppt.py`，旧入口标为 compatibility |
| 过早拆 `humanize_ppt_v2.py` 引入 bug | 本轮不拆，只记录下一轮模块化计划 |
| 本机没 pytest 导致误判 | 把缺依赖记录为环境问题，并补 smoke check |
| 新版本范围膨胀 | Office Hours 后再决定是否发版，默认不新增功能 |

---

## 9. 审批点

建议现在先确认以下决策：

1. 是否同意新增 `scripts/humanize_ppt.py` 作为唯一推荐主入口？
2. 是否同意把 `docs/v0.*.md` 移到 `docs/versions/`？
3. 是否同意本轮不拆 `humanize_ppt_v2.py`，只做入口和文档减熵？
4. 是否同意本轮完成后优先定为 `v0.5.1` 或 `v0.6.0`，暂不冲 `v1.0`？

推荐默认答案：**全部同意，版本倾向 `v0.6.0`。**
