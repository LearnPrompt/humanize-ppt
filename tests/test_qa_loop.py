"""v0.6.4 Lane C: post-render QA loop (--qa-from, max 3 iterations).

Reads a rendered HTML, scans for failure modes, writes qa_report.md
and fix_prompt.md, tracks iteration. Caps at needs-human after 3 rounds
with remaining findings.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


BAD_A = ROOT / "tests" / "fixtures" / "qa-bad-deck-style-a.html"
BAD_B = ROOT / "tests" / "fixtures" / "qa-bad-deck-style-b.html"
GOOD_A = ROOT / "tests" / "fixtures" / "qa-good-deck-style-a.html"
# Known-good Guizang Style A sample from a real native generation pass.
# Verified properties at copy time: 10 slides, 86 data-anim occurrences,
# WebGL hero background, no [必填] residue, no low-power default.
# If Guizang updates break this sample, the regression test below
# must fail so the v0.6.4 brief writers can be updated to point at
# a different known-good checkpoint.
KNOWN_GOOD_A = ROOT / "tests" / "fixtures" / "qa-known-good-style-a.html"


SAMPLE_PLAN = [
    {"slide_id": "S01", "role": "hook", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}},
    {"slide_id": "S02", "role": "context", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}},
    {"slide_id": "S03", "role": "tension", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}},
    {"slide_id": "S04", "role": "method", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}},
    {"slide_id": "S05", "role": "proof", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}},
]


def _seed_out(out, plan=SAMPLE_PLAN):
    out.mkdir(parents=True, exist_ok=True)
    (out / "slide_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def _args(qa_from, out, renderer="guizang", style="A", max_iter=3):
    return SimpleNamespace(
        qa_from=str(qa_from),
        out=str(out),
        renderer=renderer,
        guizang_style=style,
        max_qa_iterations=max_iter,
        source=None,
        title=None,
    )


def test_qa_loop_detects_style_a_failures(tmp_path):
    out = tmp_path / "run"
    _seed_out(out)
    rc = hp.run_qa_mode(_args(BAD_A, out, style="A"))
    assert rc == 0
    report = (out / "outputs" / "qa" / "qa_report.md").read_text(encoding="utf-8")
    assert "iteration: 1" in report
    assert "placeholder-residue" in report
    assert "low-power-default" in report
    assert "webgl-canvas-missing" in report
    # data-anim-thin should be a warn (2 anims in the fixture)
    assert "data-anim-thin" in report


def test_qa_loop_emits_fix_prompt_per_finding(tmp_path):
    out = tmp_path / "run"
    _seed_out(out)
    hp.run_qa_mode(_args(BAD_A, out, style="A"))
    fix = (out / "outputs" / "qa" / "fix_prompt.md").read_text(encoding="utf-8")
    assert "# Fix Prompt" in fix
    # One fix section per failed finding
    assert "placeholder-residue" in fix
    assert "low-power-default" in fix
    assert "webgl-canvas-missing" in fix
    # Each finding has a non-empty fix instruction
    assert "Substitute all" in fix or "[必填]" in fix


def test_qa_loop_converges_when_rendered_html_fixed(tmp_path):
    out = tmp_path / "run"
    _seed_out(out)
    # Round 1: bad deck
    hp.run_qa_mode(_args(BAD_A, out, style="A"))
    iter1 = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter1["iteration"] == 1
    assert iter1["status"] == "iterate"
    assert iter1["unresolved"], "round 1 should have unresolved findings"

    # Round 2: good deck (simulating downstream skill re-render)
    hp.run_qa_mode(_args(GOOD_A, out, style="A"))
    iter2 = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter2["iteration"] == 2
    assert iter2["status"] == "pass"
    assert not iter2["unresolved"], "round 2 should be clean"


def test_qa_loop_caps_at_max_iterations_with_needs_human(tmp_path):
    out = tmp_path / "run"
    _seed_out(out)
    # Round 1
    hp.run_qa_mode(_args(BAD_A, out, style="A", max_iter=3))
    # Round 2
    hp.run_qa_mode(_args(BAD_A, out, style="A", max_iter=3))
    # Round 3
    hp.run_qa_mode(_args(BAD_A, out, style="A", max_iter=3))
    iter3 = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter3["iteration"] == 3
    assert iter3["status"] == "needs-human"
    assert iter3["unresolved"], "needs-human must still record the open findings"

    # Round 4 should not advance iteration; the loop refuses to re-enter
    hp.run_qa_mode(_args(BAD_A, out, style="A", max_iter=3))
    iter_after = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter_after["iteration"] == 3, "needs-human must short-circuit further rounds"


def test_qa_loop_detects_style_b_invented_sxx(tmp_path):
    plan = [{"slide_id": f"S{n:02d}", "role": "x", "title": "x", "message": "x", "visible_content": ["x"], "speaker_intent": "x", "media": {}} for n in range(1, 6)]
    out = tmp_path / "run"
    _seed_out(out, plan=plan)
    hp.run_qa_mode(_args(BAD_B, out, style="B"))
    report = (out / "outputs" / "qa" / "qa_report.md").read_text(encoding="utf-8")
    assert "swiss-sxx-invented-id" in report
    assert "S99" in report
    assert "swiss-sxx-count-mismatch" in report
    assert "placeholder-residue" in report


def test_qa_loop_good_fixture_passes_first_round(tmp_path):
    out = tmp_path / "run"
    _seed_out(out)
    rc = hp.run_qa_mode(_args(GOOD_A, out, style="A"))
    assert rc == 0
    iter1 = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter1["iteration"] == 1
    assert iter1["status"] == "pass"
    fail_findings = [f for f in iter1.get("unresolved", []) if f.get("severity") == "fail"]
    assert not fail_findings, f"good fixture must produce no fail findings, got {fail_findings}"


def test_qa_loop_cli_end_to_end(tmp_path):
    """Real subprocess invocation via --qa-from."""
    out = tmp_path / "cli"
    out.mkdir()
    (out / "slide_plan.json").write_text(json.dumps(SAMPLE_PLAN, ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "humanize_ppt.py"),
            "--qa-from",
            str(BAD_A),
            "--out",
            str(out),
            "--renderer",
            "guizang",
            "--guizang-style",
            "A",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["iteration"] == 1
    assert payload["status"] == "iterate"
    assert payload["fail"] >= 3
    assert (out / "outputs" / "qa" / "qa_report.md").exists()
    assert (out / "outputs" / "qa" / "fix_prompt.md").exists()
    assert (out / "outputs" / "qa" / "qa_iteration.json").exists()


def test_brief_mode_does_not_create_guizang_html_even_with_render_args(tmp_path):
    """Regression: adding --guizang-style to brief mode still produces brief-only."""
    out = tmp_path / "run"
    out.mkdir()
    sample = tmp_path / "source.md"
    sample.write_text("# test\n\n- a\n- b\n- c\n- d\n- e\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "humanize_ppt.py"),
            "--source",
            str(sample),
            "--out",
            str(out),
            "--title",
            "T",
            "--renderer",
            "guizang",
            "--guizang-style",
            "B",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert (out / "guizang-production-prompt.md").exists()
    prompt = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    assert "Style: B" in prompt
    assert "assets/template-swiss.html" in prompt
    assert not (out / "outputs" / "guizang" / "index.html").exists()


def test_qa_loop_runs_renderer_agnostic_checks_for_english_renderer(tmp_path):
    """v0.8.0: placeholder-residue is renderer-agnostic ("any" scope).

    The presentation checkup (演讲体检) must not be a no-op when pointed
    at an English renderer's output: generic residue (lorem ipsum /
    TODO / TBD) must fail, and the fix prompt must name the actual
    renderer instead of hardcoding guizang.
    """
    bad = tmp_path / "bad-en.html"
    bad.write_text(
        "<html><body><section class='slide'><h1>TODO title</h1>"
        "<p>Lorem ipsum dolor sit amet.</p></section></body></html>",
        encoding="utf-8",
    )
    out = tmp_path / "run"
    _seed_out(out)
    rc = hp.run_qa_mode(_args(bad, out, renderer="beautiful-html-templates"))
    assert rc == 0
    report = (out / "outputs" / "qa" / "qa_report.md").read_text(encoding="utf-8")
    assert "placeholder-residue" in report
    fix = (out / "outputs" / "qa" / "fix_prompt.md").read_text(encoding="utf-8")
    assert "renderer: beautiful-html-templates" in fix


def test_qa_loop_runs_english_specific_failure_modes(tmp_path):
    html = tmp_path / "bad-english.html"
    html.write_text(
        """<!doctype html><html><head><style>
        body { overflow-x: auto; font-family: serif; color: #eeeeee; background: #ffffff; }
        .term { hyphens: auto; word-break: break-all; }
        </style></head><body><section class="slide"><img src="hero.png"><p class="term">InternationalizationPlatformArchitecture</p></section></body></html>""",
        encoding="utf-8",
    )
    out = tmp_path / "run"

    rc = hp.run_qa_mode(_args(html, out, renderer="frontend-slides"))

    assert rc == 0
    report = (out / "outputs" / "qa" / "qa_report.md").read_text(encoding="utf-8")
    assert "english-horizontal-overflow" in report
    assert "english-low-contrast" in report
    assert "english-hyphenation-noise" in report
    assert "english-font-contract-missing" in report
    assert "english-image-alt-missing" in report


def test_english_specific_modes_are_registered_for_both_english_renderers():
    expected = {
        "english-horizontal-overflow",
        "english-low-contrast",
        "english-hyphenation-noise",
        "english-font-contract-missing",
        "english-image-alt-missing",
    }

    for renderer in ("frontend-slides", "beautiful-html-templates"):
        modes = hp.failure_modes_for(renderer)
        assert expected.issubset(modes)


EN_SHOWCASE_DECK = ROOT / "docs" / "showcase" / "hermes-agent-mastery" / "en" / "ppt" / "index.html"


def test_english_showcase_deck_passes_presentation_checkup(tmp_path):
    """Regression for the 2026-06-13 verified English checkup run.

    docs/showcase/hermes-agent-mastery/en/ppt/index.html (Neo-Grid Bold,
    rendered natively by beautiful-html-templates) went through a real
    --qa-from run and passed round 1. registry/renderer_registry.json
    records support_level full for beautiful-html-templates
    based on this deck; if this test fails, downgrade that support_level.
    """
    if not EN_SHOWCASE_DECK.exists():
        import pytest
        pytest.skip(f"english showcase deck missing: {EN_SHOWCASE_DECK}")
    out = tmp_path / "run"
    out.mkdir(parents=True)
    rc = hp.run_qa_mode(_args(EN_SHOWCASE_DECK, out, renderer="beautiful-html-templates"))
    assert rc == 0
    iter_data = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter_data["status"] == "pass", iter_data
    assert iter_data["renderer"] == "beautiful-html-templates"


FRONTEND_SHOWCASE_DECK = ROOT / "docs" / "showcase" / "v0.9-frontend-slides" / "ppt" / "index.html"


def test_frontend_slides_showcase_deck_passes_presentation_checkup(tmp_path):
    """Regression for the 2026-06-17 verified frontend-slides checkup run.

    docs/showcase/v0.9-frontend-slides/ppt/index.html (5-slide single-file
    zero-dep deck, rendered natively by frontend-slides) went through a real
    --qa-from run and passed round 1. registry/renderer_registry.json records
    support_level full for frontend-slides based on this deck;
    if this test fails, downgrade that support_level.
    """
    if not FRONTEND_SHOWCASE_DECK.exists():
        import pytest
        pytest.skip(f"frontend-slides showcase deck missing: {FRONTEND_SHOWCASE_DECK}")
    out = tmp_path / "run"
    out.mkdir(parents=True)
    rc = hp.run_qa_mode(_args(FRONTEND_SHOWCASE_DECK, out, renderer="frontend-slides"))
    assert rc == 0
    iter_data = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert iter_data["status"] == "pass", iter_data
    assert iter_data["renderer"] == "frontend-slides"


def test_known_good_style_a_passes_all_style_a_gates(tmp_path):
    """Regression against the verified Guizang Style A Ink Classic sample.

    If Guizang updates break this sample (or the QA loop's Style A
    checks get out of sync with the live skill), this test must fail
    so the v0.6.4 known-good pointer is updated.
    """
    if not KNOWN_GOOD_A.exists():
        # The fixture was intentionally not committed in some contexts.
        # Don't fail the test suite, but make it obvious.
        import pytest
        pytest.skip(f"known-good fixture missing: {KNOWN_GOOD_A}")

    out = tmp_path / "run"
    _seed_out(out)
    rc = hp.run_qa_mode(_args(KNOWN_GOOD_A, out, style="A"))
    assert rc == 0
    iter_data = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    fail_findings = [f for f in iter_data.get("unresolved", []) if f.get("severity") == "fail"]
    assert not fail_findings, (
        f"known-good Style A fixture produced fail findings: {fail_findings}. "
        f"Either Guizang changed and the fixture is stale, or a Style A check "
        f"is out of sync with the live skill."
    )
    # Status should be pass on a clean known-good sample
    assert iter_data["status"] == "pass", iter_data
    # Sanity: Ink Classic has 86 data-anim markers, well above the 10 warn floor.
    html = KNOWN_GOOD_A.read_text(encoding="utf-8", errors="replace")
    assert len(re.findall(r"\bdata-anim(?:ate)?\b", html)) >= 10, (
        "fixture appears stale: too few data-anim markers. "
        "Re-copy from examples/03-codex-guizang-native-ink-classic/index.html"
    )
