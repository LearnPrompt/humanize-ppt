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
    assert "--ppt-master-template" in result.stdout
    assert "ppt-master" in result.stdout


def test_v3_v4_v5_shims_propagate_nonzero_exit_on_validation_failure(tmp_path):
    """v1.1.2: humanize_ppt_v3/v4/v5 are thin compatibility shims that call
    `sys.exit(main())`, matching the stable entrypoint, so a rejected
    request (here: --out with no --source/--title) propagates main()'s
    non-zero return code as the process exit code instead of always exiting
    0 (the old bare `main()` call discarded the returned int)."""
    for name in ("humanize_ppt_v3.py", "humanize_ppt_v4.py", "humanize_ppt_v5.py"):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name), "--out", str(tmp_path / name)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert result.returncode != 0, f"{name}: expected non-zero exit, got 0 ({result.stdout + result.stderr})"


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
