# 视觉增强真实产出记录（2026-06-17）

验证 Humanize 的第二项核心能力——**视觉增强**——端到端可执行：`slide_plan.json` 的每个 `media` 槽带 `asset_path` + `prompt_hint`，下游照着产出真实文件到 asset_path。Humanize 决定*要什么、放哪*，自己不渲染；这里把《AI 工具更新，不只是功能清单》的 frontend-slides run 的媒体槽逐个填成真资产。

来源 run：`.humanize-ppt-runs/v09-frontend/`（gitignore），产出资产复制到本目录 `assets/`。

## 逐槽产出

| 槽 | kind | asset_path | 产出方式 | 结果 |
|---|---|---|---|---|
| S02 diagram | `svg-html` | s02-diagram.svg | 确定性内联 SVG（背景系统图：4 路更新 → 你的工作流 hub） | ✅ 真文件 |
| S03 image | `svg-html` | s03-image.svg | 确定性内联 SVG（张力 before/after：盯功能清单 VS 改工作流） | ✅ 真文件 |
| S04 diagram | `svg-html` | s04-diagram.svg | 确定性内联 SVG（4 步状态转移） | ✅ 真文件 |
| **S04 video** | `remotion-clip` | s04-video.mp4 | **真 Remotion 渲染**（remotion 4.0.478，10s/300 帧/1280×720，4 步逐个揭示 + 进度条，无旁白） | ✅ 626 KB mp4 |
| S05 diagram | `svg-html` | s05-diagram.svg | 确定性内联 SVG（指标：5 页 / 1 句 / 100% / 0） | ✅ 真文件 |
| **S05 video** | `remotion-clip` | s05-video.mp4 | **真 Remotion 渲染**（8s/240 帧，指标 count-up 动画，无旁白） | ✅ 429 KB mp4 |
| S05 image | `screenshot` | s05-image.png | 真实 UI 截图（渲染好的 deck S05 页，非合成） | ✅ 真截图 |
| S01 image | `gpt-photo` | s01-image.png | 合成图，需 `OPENAI_API_KEY`（本环境未设）→ 留为可执行任务，不摆拍 | ⏸ 见 s01-image.GENERATE.md |

`contact-sheet.png` 是上面 8 个槽的拼图（最后一格 S01 待生成留空）。

## 结论

- **图表（svg-html）**：确定性内联 SVG，零依赖、零外呼，4 个槽全部真出。
- **视频（remotion-clip）**：真 Remotion 渲染出两支 mp4（10s + 8s 确定性循环、无旁白），证明 `_media_production_guidance` 里"视频→remotion 系列"这条是可执行的，不是口号。Remotion 4.0.478 + 原生 compositor 本地渲染，离线可跑。
- **截图（screenshot）**：捕获真实渲染产物，不合成。
- **合成图（gpt-photo）**：诚实标注需用户 API key；命令写在 `s01-image.GENERATE.md`，槽是可执行任务而非假图。

边界不变：Humanize 决定 what/where（asset_path + prompt_hint），下游产出文件，Humanize 不渲染。这一轮证明了媒体槽是真任务、各类生成器（SVG / Remotion / 截图 / imagegen）都接得上。
