# 演讲体检记录 / Presentation checkup record — 2026-06-13

Deck: `docs/showcase/hermes-agent-mastery/en/ppt/index.html`
(Neo-Grid Bold, 11 slides, rendered natively by `beautiful-html-templates`)

Command used for each static-scan round:

```bash
python3 scripts/humanize_ppt.py \
  --qa-from docs/showcase/hermes-agent-mastery/en/ppt/index.html \
  --out docs/showcase/hermes-agent-mastery/en \
  --renderer beautiful-html-templates \
  --max-qa-iterations 3
```

Machine artifacts live in `../outputs/qa/` (`qa_report.md`, `fix_prompt.md`,
`qa_iteration.json`). This file is the human-readable round log.

## Round 1 — static scan (pre-fix deck)

- Result: **pass**, 0 fail, 0 warn.
- Applicable rule: `placeholder-residue` (renderer-agnostic since v0.8.0:
  `[必填]`, `SLIDES_HERE`, lorem ipsum, TODO, TBD). The deck contains none.
- Negative control (same day): a copy of this deck with "TODO lorem ipsum"
  injected produced 2 fail findings and a `fix_prompt.md` addressed to
  `renderer: beautiful-html-templates`. The pass is real, not a no-op.

## Screenshot review (human-eye half of the checkup, after round 1)

All 11 slides were rendered at 1280x720 via `python3 -m http.server` +
Playwright and reviewed page by page against each page's intent.

- **Finding:** the bottom-left `.pagenum` badge overlapped and cut the last
  line of bottom-left text on S02, S03, S04, S05, S06, S07, S08, S10, S11.
  What the audience saw: broken sentences such as "uires confirmation."
  (S05, should read "What requires confirmation.") and "RTIFACT -> REVIEW
  -> PUBLISH" (S07, should read "brief -> artifact -> review -> publish").
  Those pages could be looked at but not spoken from.
- **Fix applied (keeps the Neo-Grid visual system):** one CSS block in the
  deck (`Presentation checkup fix (2026-06-13)`) reserving 96px bottom
  clearance in the ten panels whose text sat behind the badge. The badge
  itself was not moved; no layout, palette, or type changes.

## Round 2 — static scan + screenshot re-review (post-fix deck)

- Static scan: **pass**, 0 fail, 0 warn (`qa_iteration.json` iteration 2).
- Screenshot re-review: all previously cut lines now render in full
  (verified S02, S03, S04, S05, S06, S07, S08, S10, S11).

## Verdict

The English leg of the checkup (`--qa-from` on a real
`beautiful-html-templates` deck) is verified end to end: scan, finding,
fix, re-check. `registry/renderer_registry.json` upgrades
`beautiful-html-templates` to `support_level: brief+qa-verified` based on
this run. `frontend-slides` stays `brief-only`: no real frontend-slides
deck has gone through the checkup yet.

Caveat, stated honestly: the **static** scan alone did not catch the badge
overlap (text overlap needs a browser render; see "Not yet in the static
scan" in `references/qa-failure-modes.md`). The catch came from the
screenshot-review half of the checkup. Both halves are part of the
methodology; only the static half is automated today.
