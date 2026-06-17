# 演讲体检记录 · frontend-slides 真实渲染产物（2026-06-17）

第一单真实 frontend-slides 渲染产物的演讲体检。兑现 v0.7/v0.8 的边界声明：「frontend-slides 维持 `brief-only`，等第一单真实渲染产物走完 `--qa-from` 再升级」。

## 链路

1. **Humanize brief**（O）：`python3 scripts/humanize_ppt.py --source examples/01-ai-tool-update/source.md --renderer frontend-slides` → 产出 `frontend-slides-production-prompt.md` + `slide_plan.json`（5 页：S01 hook / S02 context / S03 tension / S04 method / S05 proof）。
2. **下游真渲**（P，100% native）：frontend-slides skill 按 brief + slide_plan 渲染单文件零依赖 HTML deck（5 页，viewport-fitting `100vh` 不滚动，包含 `viewport-base.css` 全文，distinctive「墨研 / Ink Terminal」深色编辑×科技风，Noto Serif SC + JetBrains Mono，逐页内联 SVG 示意图）。产物：`ppt/index.html`。
3. **演讲体检**（Q，`--qa-from`）：`python3 scripts/humanize_ppt.py --qa-from <rendered>/index.html --renderer frontend-slides --max-qa-iterations 3`。

## 结果

- **第 1 轮静态扫描：pass**（0 fail / 0 warn）。对 frontend-slides 生效的是渲染器无关层的 `placeholder-residue`（scope `any`）——渲染产物里无 `[必填]` / `SLIDES_HERE` / lorem / TODO / TBD 残留。`qa_report.md` 见同目录。
- **负向对照**（证明 pass 不是空转）：把同一份产物注入 `<p>TODO: lorem ipsum placeholder</p>` 的副本再扫，`status: iterate`、`fail: 2`，正确报出占位残留。说明绿是真的扫过、能扫出问题，不是没跑。
- **截图逐页复核**（体检方法论的另一半）：1280×720 逐页截 5 张（`shots/`）。每页 `100vh` 内容完整、无文字溢出、无视口截断、无装饰元素遮挡正文，每一页都拿得出口去讲。未发现「只能看、不能讲」的页。

## 结论与 registry 更新

frontend-slides：`brief-only` → **`brief+qa-verified`**。理由与 beautiful-html-templates 同级：brief 出口可用 + 演讲体检在真实渲染产物上完整跑通（扫描通过 + 负向对照证伪 + 截图复核）。**仍不升 `full`**：`FAILURE_MODES` 里没有 frontend-slides 专属规则（当前只有渲染器无关的 `placeholder-residue`），与 beautiful 留在同一档的原因一致。

这不是承诺表，是实测表：本格背后有真实渲染产物 `ppt/index.html` 和逐页截图 `shots/`。
