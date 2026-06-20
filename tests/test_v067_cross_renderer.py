"""v0.6.7 Lane c: per-page media section in all 3 brief writers.

Before Lane c, only `write_guizang_production_brief` emitted the
machine-actionable per-page media block (asset_path + prompt_hint).
The frontend-slides and beautiful brief writers were skeletons with
hardcoded text. Lane c extracts the media block to a shared helper
and wires it into the other two writers.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


SAMPLE_PLAN = hp.build_slide_plan(
    title="T",
    text="AI Agent 入门 hook. 5 步骤方法论. 证据. 5 句话.",
    segments=[
        {"title": "hook", "body": "AI Agent 圈 7 个名词"},
        {"title": "context", "body": "建立共同背景"},
        {"title": "tension", "body": "7 词看起来都像"},
        {"title": "method", "body": "5 步骤方法论"},
        {"title": "proof", "body": "证据"},
        {"title": "takeaway", "body": "5 句话总结"},
    ],
    renderer_hint="guizang",
)


def test_guizang_brief_has_per_page_media_with_asset_paths(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_guizang_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
        style="A", theme="ink-classic",
    )
    text = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "## Per-page media decisions" in text
    assert "assets/s01-image.png" in text   # hook → gpt-photo
    assert "assets/s02-diagram.svg" in text  # context → svg-html
    assert "assets/s04-diagram.svg" in text  # method → svg-html
    assert "assets/s04-video.mp4" in text    # method → remotion-clip
    assert "assets/s05-image.png" in text   # proof → screenshot
    assert "prompt_hint" in text


def test_frontend_slides_brief_has_per_page_media(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_frontend_slides_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
    )
    text = (out / "frontend-slides-production-prompt.md").read_text(encoding="utf-8")
    assert "## Per-page media decisions" in text
    assert "assets/s01-image.png" in text
    assert "assets/s04-diagram.svg" in text
    assert "assets/s04-video.mp4" in text
    assert "prompt_hint" in text


def test_beautiful_brief_has_per_page_media(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_beautiful_html_templates_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
    )
    text = (out / "beautiful-html-templates-production-prompt.md").read_text(encoding="utf-8")
    assert "## Per-page media decisions" in text
    assert "assets/s01-image.png" in text
    assert "assets/s04-diagram.svg" in text
    assert "assets/s04-video.mp4" in text
    assert "prompt_hint" in text


def test_format_per_page_media_block_empty_plan():
    """No slides → graceful 'no slide-level media' fallback."""
    out = hp._format_per_page_media_block([])
    assert "no slide-level media" in out


def test_format_per_page_media_block_includes_asset_paths():
    block = hp._format_per_page_media_block(SAMPLE_PLAN)
    # Every slide that has a needed media must have its asset_path listed
    for slide in SAMPLE_PLAN:
        media = slide.get("media") or {}
        for kind, entry in media.items():
            if entry.get("needed"):
                assert entry["asset_path"] in block, (
                    f"{slide['slide_id']} {kind} asset_path missing"
                )


def test_format_per_page_media_block_helper_deduped():
    """The helper is the only place where media_lines + media_block should
    be constructed. Other brief writers must call _format_per_page_media_block
    instead of inlining the same loop."""
    import re
    src = (ROOT / "scripts" / "humanize_ppt_v2.py").read_text(encoding="utf-8")
    # Find the helper definition block, then strip it, then count any
    # remaining inline `media_lines = []` declarations.
    helper_start = src.find("def _format_per_page_media_block")
    helper_end = src.find("\n\n\n", helper_start)
    assert helper_start != -1, "_format_per_page_media_block helper missing"
    before = src[:helper_start]
    after = src[helper_end:]
    rest = before + after
    inline_count = len(re.findall(r"^    media_lines = \[\]$", rest, re.MULTILINE))
    assert inline_count == 0, (
        f"found {inline_count} inline `media_lines = []` declarations outside "
        f"the helper; use _format_per_page_media_block instead"
    )
