# Humanize PPT Smoke Test

Humanize PPT keeps a no-dependency smoke check for machines that do not have pytest installed yet.

## Command

```bash
python3 scripts/smoke_check.py
```

By default it writes to:

```text
/tmp/humanize-ppt-smoke
```

You can choose another output directory:

```bash
python3 scripts/smoke_check.py --out /tmp/my-humanize-ppt-smoke
```

## What it verifies

The smoke check runs the stable entrypoint:

```bash
python3 scripts/humanize_ppt.py \
  --source examples/01-ai-tool-update/source.md \
  --out /tmp/humanize-ppt-smoke \
  --title "AI 工具更新，不只是功能清单" \
  --renderer guizang \
  --no-render
```

It intentionally uses `--renderer guizang --no-render` so it does not need external template repositories, browser tooling, Playwright, or network access.

It passes only when these files exist:

```text
deck_brief.md
ast_outline.md
slide_plan.json
router_plan.json
run_manifest.json
outputs/qa/qa_report.md
```

## When to use it

Use this before release notes or README updates when:

- `python3 -m pytest` fails because pytest is not installed in the active environment;
- you only need to prove the public entrypoint still creates the core contract files;
- you want a quick check before pushing docs and directory cleanup changes.

For full validation, still run:

```bash
pytest -q
```
