import html
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pptx_qa import inspect_pptx


REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DRAWING_TABLE_URI = "http://schemas.openxmlformats.org/drawingml/2006/table"


def _write_pptx(path, slides, *, prefixed_content_types=False):
    presentation_ids = []
    presentation_rels = []
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        content_types = (
            '<ns0:Types xmlns:ns0="http://schemas.openxmlformats.org/package/2006/content-types"/>'
            if prefixed_content_types
            else '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
        )
        zf.writestr("[Content_Types].xml", content_types)
        for index, spec in enumerate(slides, 1):
            presentation_ids.append(f'<p:sldId id="{255 + index}" r:id="rId{index}"/>')
            presentation_rels.append(
                f'<Relationship Id="rId{index}" Type="{OFFICE_REL}/slide" Target="slides/slide{index}.xml"/>'
            )
            if spec.get("editable", True):
                shape = f"""
                <p:sp><p:nvSpPr/><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>
                  <a:p><a:r><a:t>{html.escape(spec.get('text', ''))}</a:t></a:r></a:p>
                </p:txBody></p:sp>"""
            else:
                shape = '<p:pic><p:nvPicPr/><p:blipFill/><p:spPr/></p:pic>'
            if spec.get("native_object"):
                shape += f'<p:graphicFrame><a:graphic><a:graphicData uri="{DRAWING_TABLE_URI}"/></a:graphic></p:graphicFrame>'
            transition = "<p:transition/>" if spec.get("transition", True) else ""
            zf.writestr(
                f"ppt/slides/slide{index}.xml",
                f"""<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                  <p:cSld><p:spTree>{shape}</p:spTree></p:cSld>{transition}
                </p:sld>""",
            )

            slide_rels = []
            note = spec.get("note")
            if note is not None:
                slide_rels.append(
                    f'<Relationship Id="rIdNotes" Type="{OFFICE_REL}/notesSlide" Target="../notesSlides/notesSlide{index}.xml"/>'
                )
                zf.writestr(
                    f"ppt/notesSlides/notesSlide{index}.xml",
                    f"""<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                      xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                      <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{html.escape(note)}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>
                    </p:notes>""",
                )
            if spec.get("broken_relationship"):
                slide_rels.append(
                    f'<Relationship Id="rIdBroken" Type="{OFFICE_REL}/image" Target="../media/missing.png"/>'
                )
            zf.writestr(
                f"ppt/slides/_rels/slide{index}.xml.rels",
                f'<Relationships xmlns="{REL_NS}">{"".join(slide_rels)}</Relationships>',
            )

        zf.writestr(
            "ppt/presentation.xml",
            f"""<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:r="{OFFICE_REL}"><p:sldIdLst>{''.join(presentation_ids)}</p:sldIdLst></p:presentation>""",
        )
        zf.writestr(
            "ppt/_rels/presentation.xml.rels",
            f'<Relationships xmlns="{REL_NS}">{"".join(presentation_rels)}</Relationships>',
        )


PLAN = [
    {
        "slide_id": "S01",
        "title": "Alpha",
        "message": "Alpha message",
        "visible_content": ["Alpha evidence"],
        "speaker_intent": "Explain Alpha",
        "media": {},
    },
    {
        "slide_id": "S02",
        "title": "Beta",
        "message": "Beta message",
        "visible_content": ["Beta evidence"],
        "speaker_intent": "Explain Beta",
        "media": {},
    },
]


def test_native_pptx_with_notes_editable_shapes_and_transitions_passes(tmp_path):
    pptx = tmp_path / "good.pptx"
    _write_pptx(
        pptx,
        [
            {"text": "Alpha message and evidence", "note": "Explain Alpha clearly"},
            {"text": "Beta message and evidence", "note": "Explain Beta clearly"},
        ],
    )

    result = inspect_pptx(pptx, PLAN)

    failures = [item for item in result["findings"] if item["severity"] == "fail"]
    assert failures == []
    assert result["stats"]["slide_count"] == 2
    assert result["stats"]["notes_count"] == 2
    assert result["stats"]["editable_shape_count"] >= 2


def test_prefixed_content_types_root_is_rejected_for_office_interop(tmp_path):
    pptx = tmp_path / "prefixed-content-types.pptx"
    _write_pptx(
        pptx,
        [{"text": "Alpha message and evidence", "note": "Explain Alpha clearly"}],
        prefixed_content_types=True,
    )

    result = inspect_pptx(pptx, PLAN[:1])

    package_findings = [
        item for item in result["findings"] if item["id"] == "pptx-package-invalid"
    ]
    assert len(package_findings) == 1
    assert "prefixed root namespace" in package_findings[0]["evidence"]


def test_pptx_checker_detects_native_contract_failures(tmp_path):
    pptx = tmp_path / "bad.pptx"
    _write_pptx(
        pptx,
        [
            {
                "text": "TODO title",
                "note": None,
                "transition": False,
                "broken_relationship": True,
            },
            {"editable": False, "note": None, "transition": False},
        ],
    )

    extra_plan = [*PLAN, {"slide_id": "S03", "title": "Gamma", "speaker_intent": "Explain Gamma", "media": {}}]
    result = inspect_pptx(pptx, extra_plan)
    ids = {item["id"] for item in result["findings"]}

    assert "pptx-slide-count-mismatch" in ids
    assert "pptx-placeholder-residue" in ids
    assert "pptx-slide-empty" in ids
    assert "pptx-flattened-slide" in ids
    assert "pptx-missing-speaker-notes" in ids
    assert "pptx-broken-relationship" in ids
    assert "pptx-transition-missing" in ids


def test_native_table_expectation_is_checked_only_when_requested(tmp_path):
    pptx = tmp_path / "table.pptx"
    _write_pptx(pptx, [{"text": "Alpha table", "note": "Explain Alpha", "native_object": False}])
    plan = [{
        "slide_id": "S01",
        "title": "Alpha",
        "speaker_intent": "Explain Alpha",
        "media": {"diagram": {"needed": True, "kind": "html-table"}},
    }]

    normal = inspect_pptx(pptx, plan, require_native_objects=False)
    strict = inspect_pptx(pptx, plan, require_native_objects=True)

    assert "pptx-native-object-missing" not in {item["id"] for item in normal["findings"]}
    assert "pptx-native-object-missing" in {item["id"] for item in strict["findings"]}


def test_ppt_master_qa_cli_runs_end_to_end(tmp_path):
    pptx = tmp_path / "good.pptx"
    _write_pptx(
        pptx,
        [
            {"text": "Alpha message and evidence", "note": "Explain Alpha clearly"},
            {"text": "Beta message and evidence", "note": "Explain Beta clearly"},
        ],
    )
    out = tmp_path / "humanize-run"
    out.mkdir()
    (out / "slide_plan.json").write_text(json.dumps(PLAN), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "humanize_ppt.py"),
            "--qa-from", str(pptx),
            "--out", str(out),
            "--renderer", "ppt-master",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    iteration = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "pptx"
    assert payload["status"] == "pass"
    assert iteration["renderer"] == "ppt-master"
    assert iteration["artifact_kind"] == "pptx"


def test_ppt_master_qa_loop_emits_native_fix_prompt_then_converges(tmp_path):
    bad = tmp_path / "bad.pptx"
    good = tmp_path / "good.pptx"
    _write_pptx(
        bad,
        [
            {"text": "TODO Alpha", "note": None, "transition": False},
            {"editable": False, "note": None, "transition": False},
        ],
    )
    _write_pptx(
        good,
        [
            {"text": "Alpha message and evidence", "note": "Explain Alpha clearly"},
            {"text": "Beta message and evidence", "note": "Explain Beta clearly"},
        ],
    )
    out = tmp_path / "loop"
    out.mkdir()
    (out / "slide_plan.json").write_text(json.dumps(PLAN), encoding="utf-8")

    base = [
        sys.executable,
        str(ROOT / "scripts" / "humanize_ppt.py"),
        "--out", str(out),
        "--renderer", "ppt-master",
    ]
    first = subprocess.run(
        [*base, "--qa-from", str(bad)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert first.returncode == 0, first.stderr
    assert json.loads(first.stdout)["status"] == "iterate"
    fix_prompt = (out / "outputs" / "qa" / "fix_prompt.md").read_text(encoding="utf-8")
    assert "rendered PPTX" in fix_prompt
    assert "PPT Master's author source" in fix_prompt

    second = subprocess.run(
        [*base, "--qa-from", str(good)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert second.returncode == 0, second.stderr
    payload = json.loads(second.stdout)
    iteration = json.loads((out / "outputs" / "qa" / "qa_iteration.json").read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert iteration["iteration"] == 2
    assert iteration["unresolved"] == []
