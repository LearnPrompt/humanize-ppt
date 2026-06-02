"""v0.6.4: beautiful-html-templates production brief is brief-only.

The next agent must follow beautiful-html-templates/SKILL.md natively.
Humanize never copies templates or injects sections.
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
        "title": "Hermes",
        "message": "ship agent teams",
        "visible_content": ["ship agent teams"],
        "speaker_intent": "grab",
    },
]


def _run(out, language="en"):
    return hp.write_beautiful_html_templates_production_brief(
        out,
        title="Hermes Agent Mastery",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language=language,
    )


def test_beautiful_brief_writes_prompt(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    result = _run(out)
    assert result["status"] == "brief-written"
    assert (out / "beautiful-html-templates-production-prompt.md").exists()
    assert not (out / "outputs" / "beautiful" / "selected" / "index.html").exists()
    assert not (out / "outputs" / "beautiful" / "previews" / "index.html").exists()


def test_beautiful_brief_references_skill_md(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    _run(out)
    prompt = (out / "beautiful-html-templates-production-prompt.md").read_text(encoding="utf-8")
    assert "beautiful-html-templates/SKILL.md" in prompt
    assert "Hermes Agent Mastery" in prompt
    assert "Language: en" in prompt
