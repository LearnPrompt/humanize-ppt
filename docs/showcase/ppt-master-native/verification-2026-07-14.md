# Bilingual PPT Master native showcase verification — 2026-07-14

## Scope and version boundary

- Pull request: `LearnPrompt/humanize-ppt#10`
- Humanize PR base: `938bcd53158494daab523ea15d43d06d7de3278d`
- Humanize implementation head before these showcase/docs additions: `a26adefd5d86c5e2bed8c0704a06e76767e34eed`
- PPT Master export baseline: `b0beba5b659c664bdbf0c07227fbdee313698dd7`

English was already a `full` renderer path before v1.1. The new evidence here is the PPT Master native editable `.pptx` delivery path in both Chinese and English, not a new or reduced English-support tier.

## Before/after regression check

The PR implementation diff before the showcase additions changes `SKILL.md`, documentation, reference material, and version-metadata tests. It does not modify the Humanize generation engine or renderer implementation. The earlier base-versus-head audit generated and compared the Chinese and English contracts and found no material output change; the full test suite passed with `122 passed`.

The two new showcases are therefore additive product evidence for the already-integrated PPT Master route. They use the same five-slide semantic structure and the same production gates; only the language copy and typography strategy intentionally differ.

## Controlled bilingual inputs

- [Chinese source](source/showcase-zh.md)
- [English source](source/showcase-en.md)
- Both sources produce five pages: title, ownership boundary, production chain, native-delivery contents, and bilingual-path conclusion.
- Both decks use the same 16:9 dark-tech system, design-confirmation gate, native export path, Fade transitions, and Humanize PPTX checkup.

## Delivered artifacts

| Language | PPTX | Rendered preview |
|---|---|---|
| Chinese | [humanize-ppt-master-showcase-zh.pptx](zh/humanize-ppt-master-showcase-zh.pptx) | [preview.png](zh/preview.png) |
| English | [humanize-ppt-master-showcase-en.pptx](en/humanize-ppt-master-showcase-en.pptx) | [preview.png](en/preview.png) |

The previews are contact sheets rendered from the committed PPTX files with LibreOffice. For validation only, `Microsoft YaHei` was locally mapped to `PingFang SC`; the PPTX packages themselves retain `Microsoft YaHei`, `Arial`, and `Consolas` for PowerPoint compatibility. LibreOffice's narrow centered-text-box behavior can render very short labels more tightly than PowerPoint, but it did not hide or flatten slide content.

## Native OOXML inspection

| Check | Chinese | English |
|---|---:|---:|
| Slides | 5 | 5 |
| Speaker-note pages | 5 | 5 |
| Fade transitions | 5 | 5 |
| Native editable shapes | 238 | 244 |
| Picture elements | 0 | 0 |
| Packaged media files | 0 | 0 |
| Timing/animation trees | 0 | 0 |

Both files are native DrawingML presentations rather than flattened slide images. Text, vector shapes, diagrams, and notes remain editable in PowerPoint.

## PPT Master and Humanize QA

For each deck:

- PPT Master's SVG quality check: `5 passed / 0 warnings / 0 errors`, with no spec-lock drift.
- PPT Master export: `5/5` native pages, `5/5` notes, Fade transition, no skipped pages.
- Humanize PPTX checkup: passed on iteration 1 with `0 fail / 1 warn`.
- The single non-blocking warning is `pptx-speaker-intent-drift`: the five real notes pages do not lexically repeat the generated Humanize speaker-intent text. It is not a rendering, package-integrity, editability, or bilingual-support failure.

## Merge decision

The original PR remains non-regressive for existing Chinese and English output, and the new bilingual showcases verify the PPT Master native route with real editable artifacts. The evidence supports merging PR #10 after the repository test suite and PR checks remain green.
