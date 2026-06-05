"""v0.6.4: frontend-slides production brief is brief-only.

The next agent must follow frontend-slides/SKILL.md natively.
Humanize never opens the frontend-slides template.
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


def _run(out):
    return hp.write_frontend_slides_production_brief(
        out,
        title="Hermes Agent Mastery",
        plan=SAMPLE_PLAN,
        source=Path("source.md"),
        language="en",
    )


def test_frontend_slides_brief_writes_prompt(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    result = _run(out)
    assert result["status"] == "brief-written"
    assert (out / "frontend-slides-production-prompt.md").exists()
    assert not (out / "outputs" / "frontend-slides" / "index.html").exists()


def test_frontend_slides_brief_references_skill_md(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    _run(out)
    prompt = (out / "frontend-slides-production-prompt.md").read_text(encoding="utf-8")
    assert "frontend-slides/SKILL.md" in prompt
    assert "Hermes Agent Mastery" in prompt
    assert "Language: en" in prompt
