# PPT Master native compatibility verification — 2026-07-10

## Versions

- Humanize baseline: `a4ee3c62e86a5cdc6042ffc4ce08a2ea8f83ac12`
- PPT Master: `b0beba5b659c664bdbf0c07227fbdee313698dd7`
- Template-fill interop was verified on that PPT Master baseline plus the worktree fix that serializes `[Content_Types].xml` with its content-types namespace as the default namespace.
- macOS system Python was `3.9.6` and could not import current PPT Master annotations. Validation used Python `3.12`; Pillow-dependent export used the Codex workspace Python `3.12.13` with Pillow `12.2.0`.

## Brief and contract checks

Humanize generated a `ppt-master` route from `tests/fixtures/v066-source.md` with:

- `ppt-master-production-prompt.md`
- `ppt-master-source.md`
- disposable `outputs/ppt-master-handoff/` source copies for PPT Master's mandatory `import-sources --move` main-pipeline rule
- `commands/ppt-master-agent.md`
- a router entry for `main-svg-pipeline`
- native-object, transition, animation, visual-review, and raw-template route settings

The raw `.pptx` template test independently resolved to `template-fill-pptx`, used `--copy` for the user's source/template, required `fill_plan.json` to remain `draft` until page-sequence review, and explicitly forbade the SVG template route.

PPT Master's style gate is not duplicated. `--renderer ppt-master --style-gallery` delegates to PPT Master's mandatory three-stage Confirm UI and its native visual-style previews.

## Real native export

Source project: PPT Master's bundled `examples/ppt169_general_dark_tech_claude_code_auto_mode`, copied into an isolated ignored project directory before export.

Gates and results:

1. `project_manager.py validate` — project structure complete.
2. `svg_quality_checker.py` — 10 SVGs, 0 errors, 10 warning-bearing pages. Warnings were the bundled example's font/spec-lock drift plus a font-resolver import warning; none blocked export.
3. `total_md_split.py` — 10 SVGs matched 10 note sections; 10/10 note files generated.
4. `finalize_svg.py` — 28 icons embedded, 4 images aligned/embedded, 44 rounded rectangles converted.
5. `svg_to_pptx.py -t fade` — 10/10 pages exported as native DrawingML, 10/10 speaker notes embedded, Fade transition enabled, 0 failed pages.

The generated PPTX was 515 KB. The binary is a disposable verification artifact and is not committed to this repository.

## Humanize PPTX presentation checkup

The real PPTX was fed back through:

```bash
python3 scripts/humanize_ppt.py \
  --qa-from <native-deck.pptx> \
  --out <humanize-run> \
  --renderer ppt-master \
  --ppt-master-transition fade \
  --max-qa-iterations 3
```

Result:

- status: `pass` on iteration 1
- failures: `0`
- warnings: `1` (`pptx-speaker-intent-drift` on S04 and S08; semantic notes existed, but lexical overlap with the test plan was weak)
- slides: `10`
- slides with meaningful notes: `10`
- editable shape/group/table/chart containers: `399`
- broken slide relationships: `0`
- native-object count: `0` because this export did not request `--native-objects`

The negative OOXML fixture separately proved that the checker is not a no-op: it detects placeholder residue, empty slides, flattened slides, missing notes, missing transitions, broken relationships, and page-count mismatch.

## Real native template-fill export

The raw-template route was also exercised end to end, rather than counted from its production brief alone.

- Humanize generated a real five-page AST contract and the `template-fill-pptx` production prompt.
- Source template: the 10-page native DrawingML deck from the main-route verification above.
- The selected template layouts were source slides 1–5; every exposed text slot was mapped from the Humanize story.
- `analysis/fill_plan.json` deliberately remained `status: draft`. This internal smoke test used PPT Master's documented `apply --force` recovery/debug switch; it is not evidence of user approval and does not weaken the real workflow's blocking review gate.
- `check-plan`: `81 ok / 0 warn / 0 error`.
- `apply --transition fade --force`: five native slides exported with five speaker-note pages.
- `validate`: `7 ok / 0 warn / 0 error`.
- LibreOffice headless opened the final package and rendered all five pages to PDF. A visual pass confirmed the five layouts remained intact with no clipping in the final 120-DPI inspection.
- Humanize PPTX checkup passed on iteration 1 with `0 fail / 0 warn`: 5 slides, 5 meaningful notes pages, 199 editable shape/group/table/chart containers, and no broken relationships.

The first template-fill export exposed a real interop defect: ElementTree emitted the content-types root as `<ns0:Types>`. The XML namespace is semantically equivalent, so PPT Master's own read-back and Python OOXML readers accepted it, but LibreOffice rejected the whole presentation. PPT Master now serializes this part as `<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">`; a dedicated unit test protects the namespace restoration, and Humanize's `pptx-package-invalid` check independently rejects the prefixed root shape before delivery.

Final automated checks: Humanize `122 passed`; PPT Master template-fill namespace regression `1 passed`; both repositories passed `compileall` and `git diff --check`.

## Honest boundary

- OOXML inspection verifies package integrity and structural/native editability. Browser-rendered collision, clipping, and visual rhythm remain PPT Master's own `svg_quality_checker` plus its explicit opt-in `visual-review` workflow.
- Humanize Remotion/HyperFrames MP4 slots have no automatic one-to-one embedded-video mapping in PPT Master. The production contract requires an explicit fallback: native PowerPoint motion, static keyframe, or narrated/video-export route.
- A raw `.pptx` template always uses PPT Master's native `template-fill-pptx` workflow. Humanize does not reinterpret it as an SVG template directory.
- Template-fill v1 preserves existing native tables/charts and object-animation XML, and writes page transitions. It does not replace images or add/retime object animations; those requests require another layout, a separately approved direct-PPTX task, or an explicit `Needs-Manual` result.
