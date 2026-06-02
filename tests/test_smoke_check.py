import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_smoke_check_runs_without_pytest_dependency(tmp_path):
    out = tmp_path / "smoke"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "smoke_check.py"),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "smoke check passed" in result.stdout
    for relative in [
        "deck_brief.md",
        "ast_outline.md",
        "slide_plan.json",
        "router_plan.json",
        "run_manifest.json",
        "outputs/qa/qa_report.md",
    ]:
        assert (out / relative).exists(), relative
    # v0.6.4 brief-only contract.
    assert (out / "guizang-production-prompt.md").exists()
    assert not (out / "outputs" / "guizang" / "index.html").exists()
