"""v0.6.7 Lane d: one-conversation install + run UX.

Each brief writer now contains a "Next agent's setup checklist" section
that tells the next agent how to verify, install-if-missing, and run
the full chain. The agent reading the brief can do everything in one
session without leaving to read external docs.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


SAMPLE_PLAN = [
    {"slide_id": "S01", "role": "hook", "title": "T", "message": "m",
     "visible_content": ["v"], "speaker_intent": "i", "media": {}},
]


# ---------------------------------------------------------------------------
# Brief writers emit the setup checklist
# ---------------------------------------------------------------------------


def test_guizang_brief_has_setup_checklist(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_guizang_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
        style="A", theme="ink-classic",
    )
    text = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "## Next agent's setup checklist" in text
    # Must contain 5 numbered steps
    for n in range(1, 6):
        assert f"{n}. **" in text, f"missing step {n}"
    # Must include verify, install, re-verify, generate-media, render
    assert "test -f ~/.agents/skills/guizang-ppt-skill" in text
    assert "git clone https://github.com/op7418/guizang-ppt-skill" in text
    assert "## Hand-off" in text  # backward-compat: still has the old hand-off section


def test_frontend_slides_brief_has_setup_checklist(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_frontend_slides_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
    )
    text = (out / "frontend-slides-production-prompt.md").read_text(encoding="utf-8")
    assert "setup checklist" in text.lower()
    assert "test -f ~/.agents/skills/frontend-slides" in text
    assert "git clone https://github.com/zarazhangrui/frontend-slides" in text


def test_beautiful_brief_has_setup_checklist(tmp_path):
    out = tmp_path / "r"
    out.mkdir()
    hp.write_beautiful_html_templates_production_brief(
        out, title="T", plan=SAMPLE_PLAN, source=Path("s.md"), language="zh",
    )
    text = (out / "beautiful-html-templates-production-prompt.md").read_text(encoding="utf-8")
    assert "setup checklist" in text.lower()
    assert "test -f ~/.agents/skills/beautiful-html-templates" in text
    assert "git clone https://github.com/zarazhangrui/beautiful-html-templates" in text


# ---------------------------------------------------------------------------
# SKILL.md has the Quick start for agents section
# ---------------------------------------------------------------------------


def test_skill_md_has_quick_start_section():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "## Quick start for agents (one-conversation flow)" in skill
    # Must reference the 3 phases
    assert "humanize-ppt" in skill
    assert "guizang-ppt-skill" in skill
    assert "--preview-outline" in skill
    assert "--confirm-outline" in skill
    assert "--qa-from" in skill


def test_skill_md_requires_skills_block_unchanged():
    """v0.6.5 set the requires-skills block; v0.6.7 must not break it."""
    import re
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    block = re.search(r"requires-skills:\s*\n((?:  \S.*\n)+)", skill)
    assert block is not None, "requires-skills frontmatter block missing"
    body = block.group(1)
    assert "guizang-ppt-skill" in body
    assert "frontend-slides" in body
    assert "beautiful-html-templates" in body
