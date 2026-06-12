"""v0.7.0: speech QA outline — audience state-transfer map HTML.

scripts/preview_outline_html.py reads slide_plan.json and writes a
single-file zero-dependency HTML page: per-slide enter-state → intent →
leave-state rows plus a state-arc summary. It is a QA artifact, not a
deck — Humanize never renders slides.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preview_outline_html as pv


SAMPLE_PLAN = [
    {"slide_id": "S01", "role": "hook", "title": "标题一", "message": "m1",
     "speaker_intent": "抓住注意力", "media": {}, "layout_hint": None},
    {"slide_id": "S02", "role": "context", "title": "标题二", "message": "m2",
     "speaker_intent": "建立共同背景", "media": {}, "layout_hint": None},
    {"slide_id": "S03", "role": "takeaway", "title": "标题三", "message": "m3",
     "speaker_intent": "收束行动", "media": {}, "layout_hint": None},
]


def test_state_rows_chain_enter_and_leave_states():
    rows = pv.state_rows(SAMPLE_PLAN)
    assert len(rows) == 3
    assert rows[0]["enter"] == pv.DECK_INITIAL_STATE
    # Each slide's enter-state is the previous slide's leave-state.
    assert rows[1]["enter"] == rows[0]["leave"]
    assert rows[2]["enter"] == rows[1]["leave"]
    assert rows[0]["leave"] == pv.ROLE_LEAVE_STATE["hook"]
    assert rows[2]["leave"] == pv.ROLE_LEAVE_STATE["takeaway"]


def test_state_arc_dedupes_consecutive_roles():
    plan = SAMPLE_PLAN[:1] + [dict(SAMPLE_PLAN[0], slide_id="S02")] + SAMPLE_PLAN[2:]
    beats = pv.state_arc(pv.state_rows(plan))
    assert beats[0] == ["钩子", 2]


def test_render_html_is_single_file_zero_dependency():
    rows = pv.state_rows(SAMPLE_PLAN)
    doc = pv.render_html("测试 deck", "slide_plan.json", rows, pv.state_arc(rows))
    # Single file: no external resources of any kind.
    for marker in ("<script src=", "<link ", "http://", "https://", "@import"):
        assert marker not in doc
    # All three rows and both deck-level states render.
    for sid in ("S01", "S02", "S03"):
        assert sid in doc
    assert pv.DECK_INITIAL_STATE in doc
    assert pv.DECK_DESIRED_STATE in doc
    assert "观众进入状态" in doc and "本页意图" in doc and "观众离开状态" in doc


def test_render_html_escapes_content():
    plan = [dict(SAMPLE_PLAN[0], title='<script>alert("x")</script>')]
    rows = pv.state_rows(plan)
    doc = pv.render_html("t", "p.json", rows, pv.state_arc(rows))
    assert "<script>alert" not in doc
    assert "&lt;script&gt;" in doc


def test_cli_writes_html_from_real_example_plan(tmp_path):
    plan_path = ROOT / "examples" / "04-preview-outline-ai-tool-update" / "slide_plan.json"
    assert plan_path.exists(), "real sample slide_plan.json missing from examples/"
    out = tmp_path / "preview-outline.html"
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preview_outline_html.py"),
         "--slide-plan", str(plan_path), "--out", str(out),
         "--title", "AI 工具更新，不只是功能清单"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["ok"] is True
    assert payload["slides"] == len(json.loads(plan_path.read_text(encoding="utf-8")))
    assert out.exists()


def test_cli_missing_plan_exits_2(tmp_path):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preview_outline_html.py"),
         "--slide-plan", str(tmp_path / "nope.json"),
         "--out", str(tmp_path / "x.html")],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert r.returncode == 2
