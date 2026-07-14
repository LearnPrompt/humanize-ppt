import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "1.1.0"


def test_release_version_metadata_is_consistent():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "humanize_ppt_v2.py").read_text(encoding="utf-8")
    registry = json.loads((ROOT / "registry" / "renderer_registry.json").read_text(encoding="utf-8"))
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    assert re.search(r"^version: 1\.1\.0$", skill, re.MULTILINE)
    assert f'VERSION = "{EXPECTED_VERSION}"' in script
    assert registry["version"] == EXPECTED_VERSION
    assert marketplace["plugins"][0]["version"] == EXPECTED_VERSION


def test_skill_frontmatter_is_valid_yaml():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", skill, flags=re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"

    meta = yaml.safe_load(match.group(1))

    assert meta["name"] == "humanize-ppt"
    assert meta["version"] == EXPECTED_VERSION
    assert isinstance(meta["description"], str)
    # Agent Skills spec caps description at 1024 characters; the detailed
    # renderer verification record lives in references/renderer-verification.md.
    assert len(meta["description"]) <= 1024
    assert "presentation checkup" in meta["description"]
    assert "演讲体检" in meta["description"]
    assert "guizang-ppt-skill" in meta["requires-skills"]
    assert "frontend-slides" in meta["requires-skills"]
    assert "ppt-master" in meta["requires-skills"]
