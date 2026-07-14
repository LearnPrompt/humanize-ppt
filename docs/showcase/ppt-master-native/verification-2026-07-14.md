# Bilingual PPT Master native showcase verification — 2026-07-14

## Scope and version boundary

- Original integration pull request: `LearnPrompt/humanize-ppt#10` (merged)
- Humanize `main` before this Showcase redesign: `dca83b7c376d5a7c83b2fff50af114a1217d44a7`
- Follow-up branch: `docs/redesign-ppt-master-showcases`
- PPT Master export baseline: `47b4f61eba6c7f818bcf486b803072579e34e68b`

English was already a `full` renderer path before v1.1. The new evidence here is the PPT Master native editable `.pptx` delivery path in both Chinese and English, not a new or reduced English-support tier.

## Before/after regression check

The PR implementation diff before the showcase additions changes `SKILL.md`, documentation, reference material, and version-metadata tests. It does not modify the Humanize generation engine or renderer implementation. The earlier base-versus-head audit generated and compared the Chinese and English contracts and found no material output change; the full test suite passed with `122 passed`.

The first paired showcases proved the route but used the same generic dark-tech visual system. This follow-up replaces only the committed PPTX/preview artifacts and their documentation; it does not change the Humanize engine or PPT Master adapter. The new decks keep the same five-slide semantic structure and production gates while intentionally using different visual systems.

## Controlled bilingual inputs

- [Chinese source](source/showcase-zh.md)
- [English source](source/showcase-en.md)
- Both sources produce five pages: title, ownership boundary, production chain, native-delivery contents, and bilingual-path conclusion.
- Both decks use the same 16:9 canvas, design-confirmation gate, native export path, Fade transitions, and Humanize PPTX checkup.
- Chinese visual style: PPT Master's Memphis Pop — cream paper, bold outlined geometry, hot pink, cyan, and yellow.
- English visual style: PPT Master's Risograph Zine — paper stock, Federal Blue and fluorescent pink, cut-paste blocks, misregistration, and halftone marks.

## Delivered artifacts

| Language | Style | PPTX | Rendered preview |
|---|---|---|---|
| Chinese | Memphis Pop | [humanize-ppt-master-showcase-zh.pptx](zh/humanize-ppt-master-showcase-zh.pptx) | [preview.png](zh/preview.png) |
| English | Risograph Zine | [humanize-ppt-master-showcase-en.pptx](en/humanize-ppt-master-showcase-en.pptx) | [preview.png](en/preview.png) |

The previews are contact sheets rendered from the committed PPTX files with LibreOffice. For validation only, `Microsoft YaHei` was locally mapped to `PingFang SC`; the PPTX packages themselves retain `Microsoft YaHei`, `Impact`, `Arial`, and `Consolas` for PowerPoint compatibility. The final cross-renderer pass checked all ten pages and replaced narrow file-name tickets with editable single-letter stage indexes where LibreOffice otherwise wrapped the final character.

## Native OOXML inspection

| Check | Chinese | English |
|---|---:|---:|
| Slides | 5 | 5 |
| Speaker-note pages | 5 | 5 |
| Fade transitions | 5 | 5 |
| Editable DrawingML containers (`p:sp` + `p:grpSp`) | 224 | 268 |
| Picture elements | 0 | 0 |
| Packaged media files | 0 | 0 |
| Timing/animation trees | 0 | 0 |

Both files are native DrawingML presentations rather than flattened slide images. Text, vector shapes, diagrams, and notes remain editable in PowerPoint.

## PPT Master and Humanize QA

For each deck:

- PPT Master's SVG quality check: `5 passed / 0 warnings / 0 errors`, with no spec-lock drift.
- PPT Master export: `5/5` native pages, `5/5` notes, Fade transition, no skipped pages.
- Humanize PPTX checkup: passed on iteration 1 with `0 fail / 0 warn`.
- LibreOffice open/render: all ten pages rendered; the committed contact sheets were generated from the final PPTX files.

## Merge decision

PR #10 is already merged and remains non-regressive for existing Chinese and English output. This follow-up changes only Showcase artifacts and documentation. With both decks passing PPT Master static checks, native export, LibreOffice rendering, Humanize PPTX checkup, and the repository suite, the redesign is safe to merge.
