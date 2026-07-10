import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "fixtures" / "v066-source.md"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "humanize_ppt.py"), *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_ppt_master_main_pipeline_brief_is_self_contained(tmp_path):
    out = tmp_path / "run"
    result = _run(
        "--source", SOURCE,
        "--out", out,
        "--title", "Native PPTX",
        "--renderer", "ppt-master",
        "--ppt-master-visual-style", "swiss-minimal",
        "--ppt-master-native-objects",
        "--ppt-master-animation", "auto",
        "--ppt-master-animation-trigger", "on-click",
        "--ppt-master-visual-review",
        "--skip-install-check",
    )

    assert result.returncode == 0, result.stderr
    prompt = (out / "ppt-master-production-prompt.md").read_text(encoding="utf-8")
    source_contract = (out / "ppt-master-source.md").read_text(encoding="utf-8")
    router = json.loads((out / "router_plan.json").read_text(encoding="utf-8"))

    assert "Route: `main-svg-pipeline`" in prompt
    assert "mandatory three-stage Strategist confirmation" in prompt
    assert "PPT_MASTER_PYTHON=" in prompt
    assert "assert sys.version_info >= (3, 10)" in prompt
    assert f'"$PPT_MASTER_PYTHON" "{ROOT / "scripts" / "humanize_ppt.py"}" --qa-from' in prompt
    assert "--native-objects" in prompt
    assert "-a auto --animation-trigger on-click" in prompt
    assert "workflows/visual-review.md" in prompt
    assert "+  " not in prompt
    assert "Speaker intent:" in source_contract
    assert "## Per-slide contract" in source_contract
    assert (out / "outputs" / "ppt-master-handoff" / "ppt-master-source.md").exists()
    assert (out / "outputs" / "ppt-master-handoff" / "original-source.md").exists()
    assert router["primary_renderer"] == "ppt-master"
    route = next(item for item in router["routes"] if item["id"] == "ppt-master")
    assert route["ppt_master_route"] == "main-svg-pipeline"
    assert route["native_objects"] is True


def test_raw_pptx_template_uses_native_template_fill_route(tmp_path):
    out = tmp_path / "run"
    template = tmp_path / "brand-template.pptx"
    template.write_bytes(b"test fixture path only")

    result = _run(
        "--source", SOURCE,
        "--out", out,
        "--title", "Template Fill",
        "--ppt-master-template", template,
        "--ppt-master-native-objects",
        "--ppt-master-animation", "auto",
        "--ppt-master-visual-review",
        "--skip-install-check",
    )

    assert result.returncode == 0, result.stderr
    prompt = (out / "ppt-master-production-prompt.md").read_text(encoding="utf-8")
    assert "Route: `template-fill-pptx`" in prompt
    assert "workflows/template-fill-pptx.md" in prompt
    assert "--copy" in prompt
    assert "Do not convert this raw template through SVG" in prompt
    assert "status: draft" in prompt
    assert "`--transition fade`" in prompt
    assert "Do not pass main-pipeline `-a` or `--native-objects` flags" in prompt
    assert "cannot replace images" in prompt
    assert "does not add or retime object animations" in prompt
    assert "render the final PPTX through an office consumer" in prompt
    native_export = prompt.split("## Native export", 1)[1].split(
        "## Humanize presentation checkup", 1
    )[0]
    assert "-t fade" not in native_export


def test_ppt_master_style_gallery_delegates_to_native_confirm_ui(tmp_path):
    out = tmp_path / "style-gate"
    result = _run(
        "--source", SOURCE,
        "--out", out,
        "--title", "Native Style Gate",
        "--renderer", "ppt-master",
        "--style-gallery",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    plan = json.loads((out / "style_gallery_plan.json").read_text(encoding="utf-8"))
    command = (out / "commands" / "style-gallery" / "ppt-master-confirm-ui.md").read_text(encoding="utf-8")

    assert payload["stopped_at"] == "ppt-master-style-gate"
    assert plan["mode"] == "downstream-confirm-ui"
    assert "Stage 1" in command
    assert "--renderer ppt-master" in plan["reinjection_command"]
    assert not (out / "style_gallery.html").exists()


def test_ppt_master_presenter_and_export_flags_stay_native(tmp_path):
    out = tmp_path / "native-completion"
    result = _run(
        "--source", SOURCE,
        "--out", out,
        "--title", "Native Completion",
        "--renderer", "ppt-master",
        "--presenter",
        "--export-adapter",
        "--skip-install-check",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    router = json.loads((out / "router_plan.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in router["routes"]}

    assert payload["ok"] is True
    assert "html-ppt" not in by_id
    assert by_id["ppt-master"]["native_presenter"] is True
    assert by_id["export-adapter"]["status"] == "delegated"
    assert by_id["export-adapter"]["actual_output"].endswith("outputs/ppt-master-rendered/deck.pptx")


def test_explicit_incompatible_ppt_master_python_is_rejected(tmp_path):
    result = _run(
        "--source", SOURCE,
        "--out", tmp_path / "bad-python",
        "--title", "Bad Python",
        "--renderer", "ppt-master",
        "--ppt-master-python", tmp_path / "missing-python",
    )

    assert result.returncode == 2
    assert "must be Python 3.10 or newer" in result.stderr
