# OPC Workflow

## O — Outline Director

Humanize PPT consumes raw material and outputs the AST production contract:

- `deck_brief.md`
- `ast_outline.md`
- `slide_plan.json`
- `speaker_intent.md`
- `asset_manifest.md`
- `video_slots.json`

## P — Presentation Production

V0.3 routes to one primary renderer and optional post-processing adapters. The `beautiful-html-templates` route now renders real preview-first artifacts.

| Route | Best for |
|---|---|
| `guizang` | Chinese stable HTML PPT, magazine / Swiss style, screenshots and image framing |
| `beautiful-html-templates` | preview-first style exploration with 34 templates and `design.md` contracts |
| `html-ppt` | full-deck templates, presenter mode, speaker scripts, rich themes and animations |
| `frontend-slides` | PPTX conversion, style discovery, viewport fitting, deploy/export references |

### Router-first path

```text
Humanize PPT → router_plan.json → commands/*.md → outputs/<renderer>/
```

Downstream renderers consume the AST contract, not raw source, unless a command explicitly permits it.

## C — Complete / Control

Post-processing adapters:

- `HyperFrames Video Adapter`
- `Presenter Adapter`
- `Deploy Adapter`
- `Deck QA`

Presenter mode is not a style. It is added after a deck is produced.
