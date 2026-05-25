# Humanize PPT Release Readiness Checklist

**Date:** 2026-05-25  
**Scope:** Directory simplification, stable entrypoint, README cleanup, and smoke verification.  
**Recommended version:** `v0.6.0`

## Conclusion

This cleanup is more than a patch-level typo/doc fix because it changes the public command users should run:

- new stable entrypoint: `scripts/humanize_ppt.py`;
- README now recommends one path instead of versioned runner archaeology;
- historical V0.x notes are archived under `docs/versions/`;
- no-dependency smoke check is available through `scripts/smoke_check.py`.

Recommendation: ship as `v0.6.0` after remote sync and GitHub Pages verification. Do not call it `v1.0.0` yet because the single-entry full delivery loop still depends on template selection and selected-template follow-up.

## Release candidate checklist

Before tagging or publishing:

- [ ] `git status --short` is clean.
- [ ] `python3 scripts/humanize_ppt.py --help` works.
- [ ] `python3 scripts/humanize_ppt_v5.py --help` still works for compatibility.
- [ ] `python3 scripts/smoke_check.py` passes.
- [ ] `pytest -q` passes in an environment with pytest.
- [ ] `grep -R "docs/v0\." -n README.md README.en.md SKILL.md docs --exclude-dir=plans` has no output.
- [ ] README examples only recommend `scripts/humanize_ppt.py`.
- [ ] Historical version docs live under `docs/versions/`.
- [ ] Generated run artifacts are not committed.
- [ ] GitHub remote is synced before tag/release.
- [ ] GitHub Pages source and live page are verified after push.

## Suggested release notes

### Added

- Added `scripts/humanize_ppt.py` as the stable recommended entrypoint.
- Added `scripts/smoke_check.py` for no-dependency core contract validation.
- Added `docs/smoke-test.md` with reproducible smoke-check instructions.
- Added this release-readiness checklist.

### Changed

- Simplified README and README.en around the current recommended workflow.
- Moved historical V0.x notes into `docs/versions/`.
- Updated `SKILL.md` references to the new historical docs location.

### Kept compatible

- Kept `scripts/humanize_ppt_v1.py` through `scripts/humanize_ppt_v5.py` as compatibility entrypoints.
- Kept existing examples, contracts, registry, demos, and GitHub Pages paths.

### Deferred

- No module split of `scripts/humanize_ppt_v2.py` in this release.
- No new renderer integration.
- No video-generation pipeline.
- No deployment-platform automation.
- No WorkBuddy/CodeBuddy team package publishing automation.

## Version decision

Use this rule:

- `v0.5.1` if only the first stable entrypoint commit ships.
- `v0.6.0` if this README cleanup, smoke check, and release checklist ship together.
- `v1.0.0` only after the single-entry workflow reliably completes preview, selected-template full deck, presenter/export, QA, and documented public verification without manual repair.

Current recommendation: `v0.6.0`.
