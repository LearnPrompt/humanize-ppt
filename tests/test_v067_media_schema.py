"""v0.6.7: media schema升级 — asset_path + prompt_hint 让 media slots
从「人类可读标签」升级为「机器可执行任务」。下游 media subagent
能直接读 asset_path 写文件，读 prompt_hint 知道要生成什么。
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


# ---------------------------------------------------------------------------
# decide_media() — 6 个 role 各自的 asset_path / prompt_hint
# ---------------------------------------------------------------------------


def test_decide_media_hook_has_image_with_asset_path():
    m = hp.decide_media("hook", "Title", "Message", [], slide_id="S01")
    img = m["image"]
    assert img["needed"] is True
    assert img["kind"] == "gpt-photo"
    assert img["asset_path"] == "assets/s01-image.png"
    assert "Slide title: Title" in img["prompt_hint"]
    assert "Open the deck" in img["prompt_hint"]
    assert img["aspect_ratio"] == "16:9"
    assert img["max_size_kb"] == 200


def test_decide_media_context_has_diagram_with_asset_path():
    m = hp.decide_media("context", "T", "M", [], slide_id="S02")
    diag = m["diagram"]
    assert diag["needed"] is True
    assert diag["kind"] == "svg-html"
    assert diag["asset_path"] == "assets/s02-diagram.svg"
    assert "Establish common ground" in diag["prompt_hint"]


def test_decide_media_method_has_diagram_and_video_with_asset_path():
    m = hp.decide_media("method", "T", "M", [], slide_id="S04")
    assert m["diagram"]["asset_path"] == "assets/s04-diagram.svg"
    assert m["video"]["asset_path"] == "assets/s04-video.mp4"
    assert m["video"]["aspect_ratio"] == "16:9"
    assert m["video"]["duration_s"] == 10


def test_decide_media_proof_has_all_three_with_asset_path():
    m = hp.decide_media("proof", "T", "M", [], slide_id="S05")
    assert m["image"]["kind"] == "screenshot"
    assert m["image"]["asset_path"] == "assets/s05-image.png"
    assert m["diagram"]["asset_path"] == "assets/s05-diagram.svg"
    assert m["video"]["duration_s"] == 8
    assert m["video"]["asset_path"] == "assets/s05-video.mp4"


def test_decide_media_takeaway_has_image_with_asset_path():
    m = hp.decide_media("takeaway", "T", "M", [], slide_id="S08")
    img = m["image"]
    assert img["needed"] is True
    assert img["asset_path"] == "assets/s08-image.svg"  # svg-html kind
    # prompt_hint encodes the role description, not the purpose
    assert "Close the deck" in img["prompt_hint"] or "Reinforce" in img["prompt_hint"]
    # purpose field still holds the original (more semantic) text
    assert img["purpose"] == "Visual summary that reinforces the closing judgment"


def test_decide_media_without_slide_id_omits_asset_path():
    m = hp.decide_media("method", "T", "M", [])  # no slide_id
    assert "asset_path" not in m["diagram"]
    assert "prompt_hint" in m["diagram"]  # prompt_hint always populated


# ---------------------------------------------------------------------------
# media_extension()
# ---------------------------------------------------------------------------


def test_media_extension_known_kinds():
    assert hp.media_extension("gpt-photo") == "png"
    assert hp.media_extension("svg-html") == "svg"
    assert hp.media_extension("screenshot") == "png"
    assert hp.media_extension("html-table") == "html"
    assert hp.media_extension("remotion-clip") == "mp4"
    assert hp.media_extension("hyperframes") == "mp4"


def test_media_extension_unknown_kind():
    assert hp.media_extension("unknown-kind") == "bin"


# ---------------------------------------------------------------------------
# build_slide_plan() — 5 张 plan 都有 machine-actionable media fields
# ---------------------------------------------------------------------------


def test_build_slide_plan_propagates_slide_id_to_media():
    plan = hp.build_slide_plan(
        title="T",
        text="AI Agent 入门 hook. 5 步骤方法论. 证据. 结论.",
        segments=[
            {"title": "hook", "body": "AI Agent 圈 7 个名词你能分清几个"},
            {"title": "context", "body": "建立共同背景"},
            {"title": "method", "body": "5 步骤方法论"},
            {"title": "proof", "body": "证据"},
            {"title": "takeaway", "body": "5 句话总结"},
        ],
        renderer_hint="guizang",
    )
    # Every slide should have media with asset_path where needed.
    for slide in plan:
        media = slide.get("media") or {}
        for kind, entry in media.items():
            if entry.get("needed"):
                assert "asset_path" in entry, f"{slide['slide_id']} {kind} missing asset_path"
                assert "prompt_hint" in entry, f"{slide['slide_id']} {kind} missing prompt_hint"
                assert entry["asset_path"].startswith(f"assets/{slide['slide_id'].lower()}-")
                assert entry["asset_path"].endswith(f"-{kind}.{hp.media_extension(entry['kind'])}")


# ---------------------------------------------------------------------------
# write_guizang_production_brief() — per-page media 段含 asset_path + prompt_hint
# ---------------------------------------------------------------------------


def test_brief_writer_emits_asset_path_per_media_slot():
    # 6 segments so build_slide_plan hits hook / context / tension / method / proof / takeaway
    plan = hp.build_slide_plan(
        title="T",
        text="AI Agent 入门 hook. 上下文. 反差. 5 步骤方法论. 证据. 5 句话总结.",
        segments=[
            {"title": "hook", "body": "AI Agent 圈 7 个名词你能分清几个"},
            {"title": "context", "body": "5 年简史"},
            {"title": "tension", "body": "7 个词看起来都像"},
            {"title": "method", "body": "5 步骤方法论"},
            {"title": "proof", "body": "证据"},
            {"title": "takeaway", "body": "5 句话总结"},
        ],
        renderer_hint="guizang",
    )
    # Sanity: 6 plan entries with expected role progression
    by_id = {p["slide_id"]: p["role"] for p in plan}
    assert by_id["S01"] == "hook"
    assert by_id["S04"] == "method"
    assert by_id["S05"] == "proof"

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "run"
        out.mkdir()
        hp.write_guizang_production_brief(
            out, title="T", plan=plan, source=Path("s.md"), language="zh",
            style="A", theme="ink-classic",
        )
        text = (out / "guizang-production-prompt.md").read_text(encoding="utf-8")

    in_section = False
    section_lines = []
    for line in text.splitlines():
        if "## Per-page media decisions" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)

    body = "\n".join(section_lines)
    # Must contain at least one asset_path per media-needed slide
    assert "image.asset_path:" in body
    assert "diagram.asset_path:" in body
    assert "video.asset_path:" in body
    # Prompt hints present
    assert "image.prompt_hint:" in body
    assert "diagram.prompt_hint:" in body
    assert "video.prompt_hint:" in body
    # Path naming follows slide_id convention
    assert "assets/s01-image.png" in body  # hook → gpt-photo
    assert "assets/s02-diagram.svg" in body  # context → svg-html
    assert "assets/s04-diagram.svg" in body  # method → svg-html
    assert "assets/s04-video.mp4" in body  # method → remotion-clip
    assert "assets/s05-image.png" in body  # proof → screenshot
    assert "assets/s05-video.mp4" in body  # proof → remotion-clip 8s


# ---------------------------------------------------------------------------
# run_preview_outline_mode() — v0.6.6 outline 也带 media asset_path
# ---------------------------------------------------------------------------


def test_outline_preview_includes_asset_path():
    # 6 segments so the 6-step role arc lands cleanly
    plan = hp.build_slide_plan(
        title="T",
        text="hook. context. tension. method. proof. takeaway.",
        segments=[
            {"title": "hook", "body": "AI Agent 圈 7 个名词"},
            {"title": "context", "body": "建立共同背景"},
            {"title": "tension", "body": "7 词看起来都像"},
            {"title": "method", "body": "5 步骤方法论"},
            {"title": "proof", "body": "证据"},
            {"title": "takeaway", "body": "5 句话总结"},
        ],
        renderer_hint="guizang",
    )
    md = hp._format_outline_preview(
        title="T", plan=plan, source_path=Path("s.md"), language="zh",
        style="A", theme="ink-classic", accent=None,
    )
    # S01 hook → image gpt-photo
    assert "assets/s01-image.png" in md
    # S02 context → diagram svg-html
    assert "assets/s02-diagram.svg" in md
    # S04 method → diagram + video
    assert "assets/s04-diagram.svg" in md
    assert "assets/s04-video.mp4" in md
    # S05 proof → all three
    assert "assets/s05-image.png" in md
    assert "assets/s05-diagram.svg" in md
    assert "assets/s05-video.mp4" in md
