"""v0.6.6: --preview-outline and --confirm-outline review-checkpoint pair.

The flag pair lets a human review the AST slice (title + body + per-page
media decisions) before the production prompt is written. Spec at
references/preview-outline-spec.md.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


SAMPLE_SOURCE = ROOT / "tests" / "fixtures" / "v066-source.md"


def _seed_source(tmp_path):
    """Create a small source markdown to feed the brief writer."""
    if not SAMPLE_SOURCE.parent.exists():
        SAMPLE_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE_SOURCE.write_text(
        "# Test Source for v0.6.6 preview-outline\n\n"
        "## 介绍\n这是一个测试源。\n\n"
        "## 起源\n这是另一段。\n\n"
        "## 横向对比\n7 概念对比表。\n\n"
        "## 收束\n5 句话总结。\n",
        encoding="utf-8",
    )


def _args(out, **over):
    base = dict(
        source=str(SAMPLE_SOURCE),
        out=str(out),
        title="T",
        qa_from=None,
        max_qa_iterations=3,
        renderer="guizang",
        style_mode="stable-first",
        selected_template=None,
        presenter_adapter=False,
        export_adapter=False,
        occasion=None,
        mood=None,
        preview_count=None,
        beautiful_repo=None,
        no_beautiful_auto_clone=False,
        presenter=False,
        no_render=False,
        guizang_style="A",
        guizang_theme="ink-classic",
        guizang_accent=None,
        research_md=None,
        skip_install_check=True,
        preview_outline=False,
        confirm_outline=False,
    )
    base.update(over)
    import argparse
    return argparse.Namespace(**base)


# ---------------------------------------------------------------------------
# Direct function-call tests
# ---------------------------------------------------------------------------


def test_format_outline_preview_includes_all_sections():
    plan = [
        {"slide_id": "S01", "role": "hook", "title": "标题一", "message": "m1",
         "visible_content": ["v1a", "v1b"], "speaker_intent": "grab",
         "media": {"image": {"needed": True, "kind": "gpt-photo"}}},
        {"slide_id": "S02", "role": "context", "title": "标题二", "message": "m2",
         "visible_content": ["v2"], "speaker_intent": "explain",
         "media": {}},
    ]
    md = hp._format_outline_preview(
        title="T", plan=plan, source_path=Path("s.md"), language="zh",
        style="A", theme="ink-classic", accent=None,
    )
    assert "# Outline preview" in md
    assert "AST slice" in md
    assert "## S01 · hook" in md
    assert "## S02 · context" in md
    assert "Title (" in md and "中文字)" in md
    assert "Body (" in md and "中文字)" in md
    assert "## Per-page media decisions" in md
    assert "image=gpt-photo" in md
    assert "## Review checklist" in md
    assert "--confirm-outline" in md


def test_format_outline_preview_uses_accent_for_style_b():
    plan = [{"slide_id": "S01", "role": "hook", "title": "T", "message": "m",
             "visible_content": ["v"], "speaker_intent": "i", "media": {}}]
    md_a = hp._format_outline_preview(
        title="T", plan=plan, source_path=Path("s.md"), language="en",
        style="A", theme="ink-classic", accent=None,
    )
    assert "Theme: ink-classic" in md_a
    md_b = hp._format_outline_preview(
        title="T", plan=plan, source_path=Path("s.md"), language="en",
        style="B", theme=None, accent="ikb",
    )
    assert "Accent: ikb" in md_b
    assert "Theme" not in md_b


# ---------------------------------------------------------------------------
# run_preview_outline_mode
# ---------------------------------------------------------------------------


def test_preview_outline_writes_markdown_and_stops(tmp_path):
    _seed_source(tmp_path)
    args = _args(tmp_path, source=str(SAMPLE_SOURCE))
    rc = hp.run_preview_outline_mode(args)
    assert rc == 0
    outline = tmp_path / "outline-preview.md"
    assert outline.exists()
    text = outline.read_text(encoding="utf-8")
    assert "AST slice" in text
    assert "Per-page media decisions" in text
    assert "Review checklist" in text
    # No brief written
    assert not (tmp_path / "guizang-production-prompt.md").exists()


def test_preview_outline_missing_source_errors(tmp_path):
    args = _args(tmp_path, source=str(tmp_path / "missing.md"))
    rc = hp.run_preview_outline_mode(args)
    assert rc == 2


def test_preview_outline_uses_research_md_when_provided(tmp_path):
    _seed_source(tmp_path)
    research = tmp_path / "hv.md"
    research.write_text(
        "# HV research\n\n## 第一段\n起源...\n\n## 第二段\n横向对比...\n",
        encoding="utf-8",
    )
    args = _args(tmp_path, source=None, research_md=str(research))
    rc = hp.run_preview_outline_mode(args)
    assert rc == 0
    text = (tmp_path / "outline-preview.md").read_text(encoding="utf-8")
    assert "hv.md" in text  # source path is recorded


# ---------------------------------------------------------------------------
# run_confirm_outline_mode
# ---------------------------------------------------------------------------


def test_confirm_outline_missing_preview_errors(tmp_path):
    _seed_source(tmp_path)
    args = _args(tmp_path, confirm_outline=True)
    rc = hp.run_confirm_outline_mode(args)
    assert rc == 2


def test_confirm_outline_stale_source_errors(tmp_path):
    _seed_source(tmp_path)
    # Run preview first
    args = _args(tmp_path)
    hp.run_preview_outline_mode(args)
    # Wait so the source mtime is older than the outline mtime, then bump source
    time.sleep(0.05)
    SAMPLE_SOURCE.write_text(
        SAMPLE_SOURCE.read_text(encoding="utf-8") + "\n\n## appended\nmore\n",
        encoding="utf-8",
    )
    # Now confirm should fail because source mtime > outline mtime
    args = _args(tmp_path, confirm_outline=True)
    rc = hp.run_confirm_outline_mode(args)
    assert rc == 2


def test_confirm_outline_fresh_source_writes_marker(tmp_path):
    _seed_source(tmp_path)
    args = _args(tmp_path)
    rc = hp.run_preview_outline_mode(args)
    assert rc == 0
    # Immediately confirm (source not modified)
    args = _args(tmp_path, confirm_outline=True)
    rc = hp.run_confirm_outline_mode(args)
    assert rc == 0
    assert (tmp_path / "preview-confirmed.json").exists()
    marker = json.loads((tmp_path / "preview-confirmed.json").read_text(encoding="utf-8"))
    assert "confirmed_at" in marker
    assert marker["outline_path"].endswith("outline-preview.md")


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------


def test_cli_preview_outline_writes_and_exits_zero(tmp_path):
    _seed_source(tmp_path)
    r = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"),
            "--source", str(SAMPLE_SOURCE),
            "--out", str(tmp_path),
            "--title", "Test",
            "--renderer", "guizang",
            "--guizang-style", "A",
            "--guizang-theme", "ink-classic",
            "--preview-outline",
            "--skip-install-check",
        ],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["stopped_at"] == "preview-outline"
    assert payload["slide_count"] >= 4
    assert (tmp_path / "outline-preview.md").exists()
    # Brief NOT written
    assert not (tmp_path / "guizang-production-prompt.md").exists()


def test_cli_confirm_without_preview_errors(tmp_path):
    _seed_source(tmp_path)
    r = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"),
            "--source", str(SAMPLE_SOURCE),
            "--out", str(tmp_path),
            "--title", "Test",
            "--renderer", "guizang",
            "--guizang-style", "A",
            "--confirm-outline",
            "--skip-install-check",
        ],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r.returncode == 2
    assert "outline-preview.md not found" in r.stderr


def test_cli_preview_then_confirm_then_brief_writes_full_chain(tmp_path):
    _seed_source(tmp_path)
    # 1. Preview
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"),
         "--source", str(SAMPLE_SOURCE), "--out", str(tmp_path),
         "--title", "Test", "--renderer", "guizang",
         "--guizang-style", "A", "--guizang-theme", "ink-classic",
         "--preview-outline", "--skip-install-check"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r1.returncode == 0
    assert (tmp_path / "outline-preview.md").exists()
    # 2. Confirm
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"),
         "--source", str(SAMPLE_SOURCE), "--out", str(tmp_path),
         "--title", "Test", "--renderer", "guizang",
         "--guizang-style", "A", "--guizang-theme", "ink-classic",
         "--confirm-outline", "--skip-install-check"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r2.returncode == 0
    assert (tmp_path / "preview-confirmed.json").exists()
    # 3. Final brief write (without --preview or --confirm).
    # v1.1.1: brief mode now guards --out before wiping it (see
    # ensure_clean_out_dir). At this point --out only holds
    # outline-preview.md / preview-confirmed.json from steps 1-2, neither of
    # which is a brief-mode marker (run_manifest.json / style_gallery_plan.json),
    # so the guard correctly asks for --force here. This mirrors real CLI
    # usage: continuing a preview/confirm session into its final brief write
    # is exactly the "I know this directory, wipe it" case --force exists for.
    r3 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"),
         "--source", str(SAMPLE_SOURCE), "--out", str(tmp_path),
         "--title", "Test", "--renderer", "guizang",
         "--guizang-style", "A", "--guizang-theme", "ink-classic",
         "--force", "--skip-install-check"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r3.returncode == 0, r3.stdout + r3.stderr
    assert (tmp_path / "guizang-production-prompt.md").exists()
