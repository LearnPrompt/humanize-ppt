"""v0.6.4: Guizang production brief must be brief-only.

Humanize PPT writes `guizang-production-prompt.md` and stops. It does
NOT produce `outputs/guizang/index.html` or any other rendered HTML.
The downstream `guizang-ppt-skill` is responsible for rendering.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


SAMPLE_PLAN = [
    {
        "slide_id": "S01",
        "role": "hook",
        "title": "AI 工具更新",
        "message": "先把获得感拉满",
        "visible_content": ["先把获得感拉满"],
        "speaker_intent": "抓住注意力",
        "media": {"image": {"needed": False}, "video": {"needed": False}, "diagram": {"needed": False}},
    },
    {
        "slide_id": "S02",
        "role": "method",
        "title": "方法",
        "message": "用任务场景组织页面",
        "visible_content": ["用任务场景组织页面"],
        "speaker_intent": "给出方法",
        "media": {"image": {"needed": True, "kind": "gpt-photo"}, "video": {"needed": False}, "diagram": {"needed": False}},
    },
]


def test_guizang_brief_writes_prompt_and_creates_no_html(tmp_path):
    out = tmp_path / "run"
    out.mkdir()

    result = hp.write_guizang_production_brief(
        out,
        title="AI 工具更新，不只是功能清单",
        plan=SAMPLE_PLAN,
        source=ROOT / "examples" / "01-ai-tool-update" / "source.md",
        language="zh",
        style="A",
    )

    assert result["status"] == "brief-written"
    assert result["style"] == "A"
    assert result["slides"] == 2
    assert Path(result["prompt"]).exists()

    # Brief file is at the run root (not under outputs/).
    assert (out / "guizang-production-prompt.md").exists()
    # No HTML is produced.
    assert not (out / "outputs" / "guizang" / "index.html").exists()
    assert not (out / "outputs").exists() or not any((out / "outputs" / "guizang").glob("index.html"))


def test_guizang_brief_references_skill_md_and_style_paths(tmp_path):
    out = tmp_path / "run"
    out.mkdir()

    hp.write_guizang_production_brief(
        out,
        title="x",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language="zh",
        style="A",
    )

    prompt = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "guizang-ppt-skill/SKILL.md" in prompt
    # Style A path table
    assert "assets/template.html" in prompt
    assert "references/layouts.md" in prompt
    assert "references/themes.md" in prompt
    # Hard rules
    assert "Do not reimplement Guizang" in prompt or "do not reimplement" in prompt.lower()
    # Style A QA gates
    assert "[必填]" in prompt
    assert "SLIDES_HERE" in prompt
    assert "canvas#bg-dark" in prompt
    assert "canvas#bg-light" in prompt
    assert "data-anim" in prompt
    # Known-good checkpoint reference
    assert "03-codex-guizang-native-ink-classic" in prompt


def test_guizang_brief_style_b_uses_swiss_paths(tmp_path):
    out = tmp_path / "run"
    out.mkdir()

    result = hp.write_guizang_production_brief(
        out,
        title="x",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language="en",
        style="B",
    )

    assert result["style"] == "B"
    prompt = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "assets/template-swiss.html" in prompt
    assert "references/layouts-swiss.md" in prompt
    assert "references/themes-swiss.md" in prompt
    assert "references/swiss-layout-lock.md" in prompt
    assert "scripts/validate-swiss-deck.mjs" in prompt


def test_guizang_brief_includes_per_page_media_decisions(tmp_path):
    out = tmp_path / "run"
    out.mkdir()

    hp.write_guizang_production_brief(
        out,
        title="x",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language="zh",
        style="A",
    )

    prompt = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "S02" in prompt
    assert "gpt-photo" in prompt


def test_guizang_brief_defaults_unknown_style_to_a(tmp_path):
    out = tmp_path / "run"
    out.mkdir()

    result = hp.write_guizang_production_brief(
        out,
        title="x",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language="zh",
        style="bogus",
    )

    assert result["style"] == "A"
