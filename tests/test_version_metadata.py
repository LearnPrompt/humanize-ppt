import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.6.5"


def test_release_version_metadata_is_consistent():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "humanize_ppt_v2.py").read_text(encoding="utf-8")
    registry = json.loads((ROOT / "registry" / "renderer_registry.json").read_text(encoding="utf-8"))

    assert re.search(r"^version: 0\.6\.5$", skill, re.MULTILINE)
    assert f'VERSION = "{EXPECTED_VERSION}"' in script
    assert registry["version"] == EXPECTED_VERSION
