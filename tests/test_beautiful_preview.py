import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import humanize_ppt_v2 as hp


def test_zh_default_route_uses_guizang_with_presenter_adapter():
    args = SimpleNamespace(
        renderer="auto",
        style_mode="stable-first",
        selected_template=None,
        presenter=False,
        presenter_adapter=True,
        export_adapter=False,
    )

    primary, routes = hp.choose_routes(args, Path("source.md"), "中文 Agent 分享内容", "zh")

    assert primary == "guizang"
    assert [route["id"] for route in routes] == ["guizang", "presenter-adapter", "qa"]
    assert routes[0]["reason"] == "中文内容且未指定风格探索，优先走guizang稳定路径。"


def test_inject_presenter_bridge_adds_guizang_deck_control():
    html = """<script>
function go(n){idx=n}

/* =============== ESC 索引视图 =============== */
go(0);
</script>"""

    bridged = hp.inject_presenter_bridge(html)

    assert "window.__goSlide = go" in bridged
    assert "presenter-goto" in bridged
    assert "preview-goto" in bridged
    assert "initialSlideParam" in bridged


def make_repo(tmp_path):
    repo = tmp_path / "beautiful"
    (repo / "runtime").mkdir(parents=True)
    (repo / "runtime" / "deck-stage.js").write_text("customElements.define('deck-stage', class extends HTMLElement {});", encoding="utf-8")
    templates = [
        ("neo-grid-bold", "Neo-Grid Bold", ["confident", "editorial"], ["developer tools", "product launch"], ["bold", "design-led"], "light", "high"),
        ("soft-editorial", "Soft Editorial", ["quiet", "editorial", "warm"], ["research synthesis"], ["literary", "considered"], "light", "medium"),
        ("broadside", "Broadside", ["dramatic", "editorial"], ["brand manifesto", "design talk"], ["graphic", "punchy"], "dark", "medium"),
        ("playful", "Playful", ["playful", "warm"], ["classroom kickoff"], ["approachable"], "light", "medium"),
    ]
    index = {"schema_version": 1, "template_count": len(templates), "templates": []}
    for slug, name, mood, occasion, tone, scheme, density in templates:
        tdir = repo / "templates" / slug
        tdir.mkdir(parents=True)
        (tdir / "template.html").write_text(
            f"""<!doctype html><html><head><title>{name}</title><script src=\"deck-stage.js\"></script></head><body><deck-stage><section class=\"slide s-cover\"><div class=\"kicker\">Old Kicker</div><h1>Old Title</h1><p>Old Subtitle</p><div class=\"pagenum\">01 / 10</div></section><section class=\"slide\"><h2>Second</h2></section></deck-stage></body></html>""",
            encoding="utf-8",
        )
        index["templates"].append({
            "slug": slug,
            "name": name,
            "tagline": f"{name} tagline",
            "mood": mood,
            "occasion": occasion,
            "tone": tone,
            "formality": "medium",
            "density": density,
            "scheme": scheme,
            "best_for": "AI tools, product launches, research decks, editorial talks",
            "avoid_for": "",
            "slide_count": 10,
        })
    (repo / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return repo


def test_select_beautiful_templates_returns_three_distinct_candidates(tmp_path):
    repo = make_repo(tmp_path)

    picked = hp.select_beautiful_templates(
        repo,
        title="AI 工具更新，不只是功能清单",
        text="AI tools, developer tools, product launch, confident editorial workflow.",
        language="zh",
        occasion="developer tools product launch",
        mood="confident editorial design-led",
        count=3,
    )

    assert len(picked) == 3
    assert len({item["slug"] for item in picked}) == 3
    assert picked[0]["slug"] == "neo-grid-bold"
    assert {"slug", "name", "score", "reason"}.issubset(picked[0].keys())


def test_write_beautiful_previews_creates_real_title_slide_previews(tmp_path):
    repo = make_repo(tmp_path)
    out = tmp_path / "run"
    plan = [{"slide_id": "S01", "message": "先把获得感拉满", "title": "AI 工具更新"}]

    result = hp.write_beautiful_previews(
        out,
        title="AI 工具更新，不只是功能清单",
        text="AI tools workflow",
        plan=plan,
        repo_path=repo,
        language="zh",
        occasion="developer tools product launch",
        mood="confident editorial design-led",
        count=3,
    )

    assert result["status"] == "rendered"
    assert len(result["previews"]) == 3
    gallery = Path(result["gallery"])
    manifest = out / "outputs" / "beautiful" / "preview_manifest.json"
    report = out / "outputs" / "beautiful" / "render_report.md"
    assert gallery.exists()
    assert manifest.exists()
    assert report.exists()

    first_preview = Path(result["previews"][0]["path"])
    html = first_preview.read_text(encoding="utf-8")
    assert "AI 工具更新" in html
    assert "先把获得感拉满" in html
    assert "Second" not in html
    assert "01 / 01" in html
    assert (first_preview.parent / "deck-stage.js").exists()


def test_write_beautiful_previews_returns_missing_when_library_absent(tmp_path):
    result = hp.write_beautiful_previews(
        tmp_path / "run",
        title="Missing Repo",
        text="",
        plan=[],
        repo_path=tmp_path / "does-not-exist",
        language="en",
        occasion=None,
        mood=None,
        count=3,
    )

    assert result["status"] == "missing-library"
    assert "index.json" in result["message"]


def test_write_beautiful_selected_deck_creates_full_deck_from_one_template(tmp_path):
    repo = make_repo(tmp_path)
    out = tmp_path / "run"
    plan = [
        {
            "slide_id": "S01",
            "role": "hook",
            "title": "AI 工具更新",
            "message": "先把获得感拉满",
            "visible_content": ["先把获得感拉满", "不要把功能更新硬拆成清单"],
            "speaker_intent": "抓住注意力",
        },
        {
            "slide_id": "S02",
            "role": "method",
            "title": "方法论",
            "message": "用反常识方法串起测试项",
            "visible_content": ["用任务场景组织页面", "保留角色分工和案例"],
            "speaker_intent": "给出方法",
        },
        {
            "slide_id": "S03",
            "role": "takeaway",
            "title": "结论",
            "message": "观众能直接复述下一步",
            "visible_content": ["模板先选中，再生成全量 deck"],
            "speaker_intent": "收束行动",
        },
    ]

    result = hp.write_beautiful_selected_deck(
        out,
        title="AI 工具更新，不只是功能清单",
        plan=plan,
        repo_path=repo,
        selected_template="neo-grid-bold",
    )

    assert result["status"] == "rendered"
    assert result["template"] == "neo-grid-bold"
    deck = Path(result["deck"])
    manifest = out / "outputs" / "beautiful" / "selected_manifest.json"
    report = out / "outputs" / "beautiful" / "render_report.md"
    assert deck == out / "outputs" / "beautiful" / "selected" / "index.html"
    assert deck.exists()
    assert manifest.exists()
    assert report.exists()

    html = deck.read_text(encoding="utf-8")
    assert "Humanize PPT · Selected Template Full Deck" in html
    assert "AI 工具更新，不只是功能清单" in html
    assert "先把获得感拉满" in html
    assert "用反常识方法串起测试项" in html
    assert "观众能直接复述下一步" in html
    assert "01 / 03" in html
    assert "02 / 03" in html
    assert "03 / 03" in html
    assert "Old Title" not in html
    assert "Second" not in html
    assert (deck.parent / "deck-stage.js").exists()

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["selected_template"] == "neo-grid-bold"
    assert data["slide_count"] == 3


def test_write_beautiful_selected_deck_returns_missing_for_unknown_template(tmp_path):
    repo = make_repo(tmp_path)

    result = hp.write_beautiful_selected_deck(
        tmp_path / "run",
        title="Missing Template",
        plan=[],
        repo_path=repo,
        selected_template="not-a-template",
    )

    assert result["status"] == "missing-template"
    assert "not-a-template" in result["message"]


def test_write_presenter_adapter_creates_presenter_shell_with_notes(tmp_path):
    out = tmp_path / "run"
    deck_dir = out / "outputs" / "beautiful" / "selected"
    deck_dir.mkdir(parents=True)
    deck_path = deck_dir / "index.html"
    deck_path.write_text("<html><body><section class='slide'>Deck</section></body></html>", encoding="utf-8")
    plan = [
        {"slide_id": "S01", "title": "开场", "message": "先把获得感拉满", "speaker_intent": "抓住注意力"},
        {"slide_id": "S02", "title": "方法", "message": "讲清楚方法", "speaker_intent": "给出路径"},
    ]

    result = hp.write_presenter_adapter(out, title="AI 工具更新", plan=plan, deck_path=deck_path)

    assert result["status"] == "rendered"
    presenter = out / "outputs" / "presenter" / "index.html"
    manifest = out / "outputs" / "presenter" / "presenter_manifest.json"
    assert presenter.exists()
    assert manifest.exists()
    html = presenter.read_text(encoding="utf-8")
    assert "Humanize PPT · Presenter Adapter" in html
    assert "../beautiful/selected/index.html?slide=1" in html
    assert "presenter-goto" in html
    assert "preview-goto" in html
    assert "CURRENT" in html
    assert "NEXT" in html
    assert "SCRIPT" in html
    assert "先把获得感拉满" in html
    assert "给出路径" in html
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["deck"] == str(deck_path)
    assert data["slide_count"] == 2


def test_write_export_adapter_creates_portable_package_and_export_script(tmp_path):
    out = tmp_path / "run"
    deck_dir = out / "outputs" / "beautiful" / "selected"
    deck_dir.mkdir(parents=True)
    deck_path = deck_dir / "index.html"
    deck_path.write_text("<html><body><section class='slide'>Deck</section></body></html>", encoding="utf-8")
    (deck_dir / "deck-stage.js").write_text("customElements.define('deck-stage', class extends HTMLElement {});", encoding="utf-8")

    result = hp.write_export_adapter(out, title="AI 工具更新", deck_path=deck_path, slide_count=3)

    assert result["status"] == "packaged"
    package = out / "outputs" / "export" / "package"
    manifest = out / "outputs" / "export" / "export_manifest.json"
    script = out / "outputs" / "export" / "export_pdf.sh"
    readme = out / "outputs" / "export" / "README.md"
    assert (package / "index.html").exists()
    assert (package / "deck-stage.js").exists()
    assert manifest.exists()
    assert script.exists()
    assert readme.exists()
    assert "playwright" in script.read_text(encoding="utf-8")
    assert "outputs/export/package/index.html" in readme.read_text(encoding="utf-8")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["deck"] == str(deck_path)
    assert data["package"] == str(package)
    assert data["slide_count"] == 3


def test_write_export_adapter_returns_missing_when_deck_absent(tmp_path):
    result = hp.write_export_adapter(
        tmp_path / "run",
        title="Missing Deck",
        deck_path=tmp_path / "missing" / "index.html",
        slide_count=0,
    )

    assert result["status"] == "missing-deck"
    assert "index.html" in result["message"]
