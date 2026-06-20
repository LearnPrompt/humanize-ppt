import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_english_renderers_are_full_with_specific_failure_modes():
    registry = json.loads((ROOT / "registry" / "renderer_registry.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in registry["renderers"]}
    expected = {
        "english-horizontal-overflow",
        "english-low-contrast",
        "english-hyphenation-noise",
        "english-font-contract-missing",
        "english-image-alt-missing",
    }

    for renderer_id in ("frontend-slides", "beautiful-html-templates"):
        item = by_id[renderer_id]
        assert item["support_level"] == "full"
        assert set(item["qa_failure_modes"]) == expected


def test_presenter_shell_is_registered_as_humanize_output_type():
    registry = json.loads((ROOT / "registry" / "renderer_registry.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in registry["renderers"]}
    presenter = by_id["presenter-adapter"]

    assert presenter["role"] == "humanize-native-presenter-shell"
    assert "slide_plan.json" in presenter["inputs"]
    assert "speaker_intent.md" in presenter["inputs"]
    assert "outputs/presenter/presenter-shell.html" in presenter["outputs"]
