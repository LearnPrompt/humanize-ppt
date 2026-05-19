# Router Rules

Humanize PPT V0.3 routes by **presentation intent**, not by a fixed downstream Skill list. Recommended renderers are pairings, not the product boundary.

## Primary renderer selection

| Signal | Route |
|---|---|
| Chinese content + stability first | `guizang` |
| User asks for Swiss / magazine style | `guizang` |
| User asks to compare styles or `--style-mode preview-first` | `beautiful-html-templates` |
| User needs presenter mode / speaker script as the main deliverable | `html-ppt` |
| Input is `.ppt` / `.pptx` | `frontend-slides` |
| User explicitly names a renderer | respect the explicit renderer |

## Post-processing routes

- Needs live talk / speaker notes → add `html-ppt` presenter route after primary deck selection.
- Needs motion / inserted video → emit `video_slots.json`; route to HyperFrames / Remotion as material producer, not as PPT replacement.
- Needs shareable URL / PDF → add deploy/export adapter after deck QA.
- Every run → add `qa` route.

## Hard boundaries

- Downstream renderers must consume `deck_brief.md`, `ast_outline.md`, `slide_plan.json`, `speaker_intent.md`, and `asset_manifest.md`; they should not consume raw source unless the command file explicitly permits it.
- Presenter mode is a post-processing adapter, not a visual style.
- Humanize PPT can be invoked alone, but it remains the router/director layer; it should not absorb every template into one monolithic renderer.
