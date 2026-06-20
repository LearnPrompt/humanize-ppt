import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_SOURCE = ROOT / "tests" / "fixtures" / "v066-source.md"


def test_stable_main_entrypoint_exposes_help():
    entrypoint = ROOT / "scripts" / "humanize_ppt.py"

    result = subprocess.run(
        [sys.executable, str(entrypoint), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "--source" in result.stdout
    assert "--out" in result.stdout
    assert "--presenter-adapter" in result.stdout


def test_module_entrypoint_can_render_presenter_shell_without_deck(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "humanize_ppt_v2",
            "--source",
            str(SAMPLE_SOURCE),
            "--out",
            str(tmp_path),
            "--title",
            "Presenter Shell Smoke",
            "--presenter-adapter",
            "--no-render",
            "--skip-install-check",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "outputs" / "presenter" / "presenter-shell.html").exists()
