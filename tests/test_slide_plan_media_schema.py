"""v0.6.4 Lane B: slide_plan.json carries Humanize's per-page media decision.

Each slide has `media: {image, diagram, video}` and `layout_hint`.
The downstream skill consumes this and produces the actual materials.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


SAMPLE_SEGMENTS = [
    {"title": "开场", "body": "先把获得感拉满，先指出大家已经疲劳：AI 工具每天都在更新。"},
    {"title": "背景", "body": "建立共同背景：说明为什么现在要听 Agent 工作流这件事。"},
    {"title": "反差", "body": "指出旧理解和真实问题之间的差距，反常识：工作流入口是否迁移。"},
    {"title": "方法", "body": "用反常识方法串起测试项。给一个具体步骤：先做 AST 大纲再交给下游 Skill。"},
    {"title": "证据", "body": "用案例和指标证明它不是口号。展示真实页面截图与对比。"},
    {"title": "结论", "body": "收束行动：观众能直接复述下一步。"},
]


def _plan():
    return hp.build_slide_plan(
        title="AI 工具更新",
        text="\n".join(s["body"] for s in SAMPLE_SEGMENTS),
        segments=SAMPLE_SEGMENTS,
        renderer_hint="guizang",
    )


def test_slide_plan_has_media_and_layout_hint_per_slide():
    plan = _plan()
    assert len(plan) >= 5
    for slide in plan:
        assert "media" in slide, slide
        assert "layout_hint" in slide, slide
        media = slide["media"]
        assert set(media.keys()) == {"image", "diagram", "video"}
        for kind in ("image", "diagram", "video"):
            assert "needed" in media[kind]
            assert "kind" in media[kind]


def test_slide_plan_media_policy_per_role():
    plan = _plan()
    by_id = {p["slide_id"]: p for p in plan}

    # S01 is hook: image needed, no diagram, no video
    s01 = by_id["S01"]
    assert s01["role"] == "hook"
    assert s01["media"]["image"]["needed"] is True
    assert s01["media"]["image"]["kind"] == "gpt-photo"
    assert s01["media"]["diagram"]["needed"] is False
    assert s01["media"]["video"]["needed"] is False
    assert s01["layout_hint"] == "S01-cover-hero"

    # S04 (method): diagram + video needed
    method_pages = [p for p in plan if p["role"] == "method"]
    assert method_pages, "expected at least one method page"
    s = method_pages[0]
    assert s["media"]["diagram"]["needed"] is True
    assert s["media"]["diagram"]["kind"] == "svg-html"
    assert s["media"]["video"]["needed"] is True
    assert s["media"]["video"]["kind"] == "remotion-clip"
    assert s["media"]["video"]["duration_s"] == 10
    assert s["layout_hint"] == "S07-process-21x9"

    # S05 (proof): all three needed
    proof_pages = [p for p in plan if p["role"] == "proof"]
    if proof_pages:
        s = proof_pages[0]
        assert s["media"]["image"]["needed"] is True
        assert s["media"]["diagram"]["needed"] is True
        assert s["media"]["video"]["needed"] is True
        assert s["layout_hint"] == "S12-proof-metrics"


def test_slide_plan_validates_against_schema():
    plan = _plan()
    schema_path = ROOT / "contracts" / "slide-plan.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    # Lightweight structural check (no jsonschema dep required).
    required_top = {"slide_id", "role", "title", "message", "speaker_intent", "media", "layout_hint"}
    media_required = {"image", "diagram", "video"}
    for slide in plan:
        missing = required_top - slide.keys()
        assert not missing, f"{slide.get('slide_id')}: missing {missing}"
        for kind in media_required:
            entry = slide["media"].get(kind) or {}
            assert "needed" in entry, f"{slide['slide_id']}.media.{kind}.needed missing"
            assert "kind" in entry, f"{slide['slide_id']}.media.{kind}.kind missing"
        assert slide["layout_hint"] is not None, f"{slide['slide_id']}.layout_hint must be set"
        # Schema description strings
        assert "id" not in slide, "legacy `id` field leaked"
    # Schema file itself declares the required set
    for required in schema["items"]["required"]:
        assert required in required_top or required == "media" or required == "layout_hint"


def test_asset_manifest_reflects_media_decisions(tmp_path):
    from pathlib import Path as P

    out = tmp_path / "run"
    out.mkdir()
    plan = _plan()
    hp.write_contracts(
        out,
        title="AI 工具更新",
        source_path=P("source.md"),
        text="x",
        plan=plan,
        language="zh",
    )
    manifest = (out / "asset_manifest.md").read_text(encoding="utf-8")
    # Should mention at least one image row, at least one diagram, at least one video
    assert "asset-s01-image" in manifest or "gpt-photo" in manifest
    # At least one diagram row from method/proof
    assert "svg-html" in manifest
    # Method page should produce a video row
    method_pages = [p for p in plan if p["role"] == "method"]
    if method_pages:
        sid = method_pages[0]["slide_id"].lower()
        assert f"asset-{sid}-video" in manifest


def test_video_slots_json_reflects_media_decisions(tmp_path):
    from pathlib import Path as P

    out = tmp_path / "run"
    out.mkdir()
    plan = _plan()
    hp.write_contracts(
        out,
        title="AI 工具更新",
        source_path=P("source.md"),
        text="x",
        plan=plan,
        language="zh",
    )
    slots = json.loads((out / "video_slots.json").read_text(encoding="utf-8"))
    method_pages = [p for p in plan if p["role"] == "method"]
    if method_pages:
        assert len(slots) >= 1
        assert slots[0]["kind"] == "remotion-clip"
        assert slots[0]["duration_seconds"] == 10
        assert slots[0]["slide_id"] == method_pages[0]["slide_id"]


def test_guizang_brief_picks_up_media_after_lane_b(tmp_path):
    """End-to-end: build_slide_plan now feeds the brief's per-page media section."""
    out = tmp_path / "run"
    out.mkdir()
    plan = hp.build_slide_plan(
        title="AI 工具更新",
        text="\n".join(s["body"] for s in SAMPLE_SEGMENTS),
        segments=SAMPLE_SEGMENTS,
        renderer_hint="guizang",
    )
    hp.write_guizang_production_brief(
        out,
        title="AI 工具更新",
        plan=plan,
        source=Path("source.md"),
        language="zh",
        style="A",
    )
    prompt = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")
    # No more "no media" for every page when role policy is satisfied.
    assert "gpt-photo" in prompt or "svg-html" in prompt or "remotion-clip" in prompt
    # Per-page media section is no longer empty for the plan we built.
    method_lines = [l for l in prompt.splitlines() if "method" in l.lower() or "remotion" in l.lower()]
    assert method_lines, "expected method-page media to surface in the brief"
