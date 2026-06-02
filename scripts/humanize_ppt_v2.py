#!/usr/bin/env python3
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = SKILL_ROOT / "registry" / "renderer_registry.json"
VERSION = "0.6.5"
BEAUTIFUL_REPO_URL = "https://github.com/zarazhangrui/beautiful-html-templates.git"
DEFAULT_ZH_PREVIEW_COUNT = 3
DEFAULT_EN_PREVIEW_COUNT = 5

ROLE_ARC = [
    ("hook", "抓住注意力：先把观众从信息疲劳里拉出来。"),
    ("context", "建立共同背景：说明为什么现在要听这件事。"),
    ("tension", "制造认知张力：指出旧理解和真实问题之间的差距。"),
    ("method", "给出方法：把复杂信息变成可执行路径。"),
    ("proof", "给出证据：用案例、步骤或指标证明它不是口号。"),
    ("takeaway", "收束行动：让观众带走一句可复述的方法。"),
]

BANNED_VISIBLE_PATTERNS = ["思考过程", "推理过程", "作为AI", "作为一个AI", "我将", "首先我需要"]


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_registry():
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {"version": VERSION, "renderers": []}


def expand_user_path(value):
    return Path(value).expanduser()


def read_source(source):
    path = Path(source).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"source not found: {path}")
    if path.suffix.lower() in {".ppt", ".pptx"}:
        return path, f"PPTX source: {path.name}\n", []
    text = path.read_text(encoding="utf-8", errors="replace")
    return path, text, markdown_segments(text)


def strip_md(line):
    line = re.sub(r"^#{1,6}\s*", "", line.strip())
    line = re.sub(r"^[-*+]\s+", "", line)
    line = re.sub(r"^\d+[.)]\s+", "", line)
    line = re.sub(r"[`*_>\[\]]", "", line)
    return line.strip()


def markdown_segments(text):
    segments = []
    current_title = None
    buffer = []

    def flush():
        nonlocal current_title, buffer
        body = " ".join(strip_md(x) for x in buffer if strip_md(x))
        if current_title or body:
            segments.append({"title": current_title or first_sentence(body), "body": body})
        current_title = None
        buffer = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^#{1,3}\s+", line):
            flush()
            current_title = strip_md(line)
        else:
            buffer.append(line)
    flush()

    if not segments:
        lines = [strip_md(x) for x in text.splitlines() if strip_md(x)]
        for i in range(0, min(len(lines), 12), 2):
            body = " ".join(lines[i : i + 2])
            segments.append({"title": first_sentence(body), "body": body})
    return [s for s in segments if s.get("title") or s.get("body")]


def first_sentence(text, fallback="未命名要点"):
    text = " ".join(text.split())
    if not text:
        return fallback
    parts = re.split(r"(?<=[。！？.!?])\s+|[。！？!?]", text)
    title = parts[0].strip() if parts else text
    return title[:42] or fallback


def detect_language(text):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk >= latin * 0.25 else "en"


def infer_audience(text, language):
    lower = text.lower()
    if any(k in lower for k in ["agent", "skill", "ai", "模型", "工具", "ppt"]):
        return "对AI工具、PPT生产、Agent工作流感兴趣的内容创作者、产品人和独立开发者。" if language == "zh" else "Creators, product builders, and independent developers interested in AI tools and agent workflows."
    return "需要快速理解主题、形成判断并采取下一步行动的听众。" if language == "zh" else "An audience that needs to understand the topic, form judgment, and take action."


def build_slide_plan(title, text, segments, renderer_hint):
    if not segments:
        segments = [{"title": title, "body": text.strip() or title}]
    selected = segments[: max(5, min(8, len(segments)))]
    while len(selected) < 5:
        selected.append(selected[-1])

    plan = []
    for i, item in enumerate(selected[:8], 1):
        role, intent = ROLE_ARC[min(i - 1, len(ROLE_ARC) - 1)]
        body = item.get("body") or item.get("title") or title
        message = first_sentence(body, fallback=item.get("title") or title)
        visible = [message]
        detail = body.replace(message, "", 1).strip(" 。，,.；;")
        if detail:
            visible.append(detail[:110])
        media = decide_media(role, title if i == 1 else (item.get("title") or message), message, visible)
        plan.append(
            {
                "slide_id": f"S{i:02d}",
                "role": role,
                "title": title if i == 1 else (item.get("title") or message)[:48],
                "message": message[:120],
                "visible_content": visible[:3],
                "speaker_intent": intent,
                "media": media,
                "layout_hint": layout_hint_for_role(role),
                "recommended_renderer": renderer_hint,
            }
        )
    return plan


# Per-role media decision. Humanize makes the call; downstream skills
# produce the actual material in their native format.
ROLE_MEDIA_POLICY = {
    "hook": {
        "image":   {"needed": True,  "kind": "gpt-photo"},
        "diagram": {"needed": False, "kind": "none"},
        "video":   {"needed": False, "kind": "none"},
    },
    "context": {
        "image":   {"needed": False, "kind": "none"},
        "diagram": {"needed": True,  "kind": "svg-html"},
        "video":   {"needed": False, "kind": "none"},
    },
    "tension": {
        "image":   {"needed": True,  "kind": "svg-html"},
        "diagram": {"needed": False, "kind": "none"},
        "video":   {"needed": False, "kind": "none"},
    },
    "method": {
        "image":   {"needed": False, "kind": "none"},
        "diagram": {"needed": True,  "kind": "svg-html"},
        "video":   {"needed": True,  "kind": "remotion-clip", "duration_s": 10},
    },
    "proof": {
        "image":   {"needed": True,  "kind": "screenshot"},
        "diagram": {"needed": True,  "kind": "svg-html"},
        "video":   {"needed": True,  "kind": "remotion-clip", "duration_s": 8},
    },
    "takeaway": {
        "image":   {"needed": True,  "kind": "svg-html"},
        "diagram": {"needed": False, "kind": "none"},
        "video":   {"needed": False, "kind": "none"},
    },
}

ROLE_LAYOUT_HINT = {
    "hook":     "S01-cover-hero",
    "context":  "S04-context-system",
    "tension":  "S06-tension-comparison",
    "method":   "S07-process-21x9",
    "proof":    "S12-proof-metrics",
    "takeaway": "S22-takeaway",
}


def layout_hint_for_role(role):
    return ROLE_LAYOUT_HINT.get(role)


def decide_media(role, title, message, visible_content):
    """Per-page media decision.

    Returns a dict shaped like the `media` field in slide-plan.schema.json.
    The downstream skill reads this and produces materials in its native
    format. Humanize never renders them.
    """
    base = {
        "image":   {"needed": False, "kind": "none"},
        "diagram": {"needed": False, "kind": "none"},
        "video":   {"needed": False, "kind": "none"},
    }
    policy = ROLE_MEDIA_POLICY.get(role)
    if not policy:
        return base

    text = " ".join([title or "", message or "", " ".join(visible_content or [])]).lower()
    for key in ("image", "diagram", "video"):
        entry = dict(policy.get(key) or {"needed": False, "kind": "none"})
        if entry.get("needed"):
            entry["purpose"] = media_purpose(role, key, text)
            entry["slot"] = media_slot(role, key)
        base[key] = entry
    return base


def media_purpose(role, kind, text):
    if kind == "image":
        if role == "hook":
            return "Set emotional anchor for the opening page"
        if role == "tension":
            return "Show before/after or contradiction visually"
        if role == "proof":
            return "Screenshot evidence of the real UI or result"
        if role == "takeaway":
            return "Visual summary that reinforces the closing judgment"
    if kind == "diagram":
        if role == "context":
            return "Show the system relationship or scope"
        if role == "method":
            return "Diagram the process / decision tree / flow"
        if role == "proof":
            return "Diagram the comparison or supporting structure"
    if kind == "video":
        if role == "method":
            return "8-12s process clip that walks through the method"
        if role == "proof":
            return "Short before/after or result clip"
    return ""


def media_slot(role, kind):
    if kind == "image":
        return f"{role}-image-16x9"
    if kind == "diagram":
        return f"{role}-diagram-21x9"
    if kind == "video":
        return f"{role}-video-16x9"
    return f"{role}-{kind}"


def write_contracts(out, title, source_path, text, plan, language):
    audience = infer_audience(text, language)
    tension = "资料很多，但能让观众听懂、记住、复述的路径不清晰。" if language == "zh" else "There is too much material and not enough audience-ready narrative path."
    goal = f"把《{title}》整理成可讲、可生成、可交付的PPT生产契约。" if language == "zh" else f"Turn '{title}' into a presentation-ready production contract."
    out.mkdir(parents=True, exist_ok=True)
    (out / "deck_brief.md").write_text(
        f"""# Deck Brief

## Title
{title}

## Source
{source_path}

## Deck Goal
{goal}

## Audience
{audience}

## Initial State
听众知道一些零散信息，但缺少清晰判断和行动路径。

## Desired State
听众能复述核心判断，理解为什么现在要做，并知道下一步怎么执行。

## Core Tension
{tension}

## Success Criteria
- 观众能用一句话说出这份PPT的核心判断。
- 每页只承担一个状态转移任务。
- 下游渲染器不直接吞原始素材，只消费Humanize PPT契约。
""",
        encoding="utf-8",
    )
    (out / "ast_outline.md").write_text(
        "# AST Outline\n\n"
        f"## Audience\n{audience}\n\n"
        "## State\n- Initial: 信息分散，缺少可讲路径。\n- Desired: 形成清晰判断，并能执行下一步。\n\n"
        "## Transfer\n"
        + "\n".join([f"- {p['slide_id']} / {p['role']}: {p['speaker_intent']}" for p in plan])
        + "\n",
        encoding="utf-8",
    )
    (out / "slide_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "speaker_intent.md").write_text(
        "\n".join(
            [
                f"## {p['slide_id']} {p['title']}\n\n- Intent: {p['speaker_intent']}\n- Say: {p['message']}\n- Avoid: 不要把模型草稿、推理过程或工具清单直接放到页面上。\n"
                for p in plan
            ]
        ),
        encoding="utf-8",
    )
    asset_rows = []
    for p in plan:
        media = p.get("media") or {}
        for kind, key in (("image", "image"), ("diagram", "diagram"), ("video", "video")):
            entry = media.get(key) or {}
            if not entry.get("needed"):
                continue
            asset_rows.append(
                f"| asset-{p['slide_id'].lower()}-{key} | {p['slide_id']} | {entry.get('kind', '?')} | {entry.get('purpose', '')} | pending |"
            )
    (out / "asset_manifest.md").write_text(
        "# Asset Manifest\n\n"
        "Each row is a Humanize-owned media decision. The downstream skill "
        "produces the material in its own native format.\n\n"
        "| asset_id | slide_id | type | purpose | status |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(asset_rows)
        + "\n",
        encoding="utf-8",
    )
    video_slots = []
    for idx, p in enumerate(plan, 1):
        video = (p.get("media") or {}).get("video") or {}
        if not video.get("needed"):
            continue
        video_slots.append(
            {
                "video_id": f"V{idx:02d}",
                "slide_id": p["slide_id"],
                "kind": video.get("kind", "remotion-clip"),
                "purpose": video.get("purpose", ""),
                "duration_seconds": int(video.get("duration_s", 10)),
                "aspect_ratio": "16:9",
                "slot": video.get("slot", f"{p['role']}-video-16x9"),
                "fallback_static": f"asset-{p['slide_id'].lower()}-diagram",
            }
        )
    (out / "video_slots.json").write_text(json.dumps(video_slots, ensure_ascii=False, indent=2), encoding="utf-8")


def choose_routes(args, source_path, text, language):
    requested = args.renderer
    suffix = source_path.suffix.lower()
    if requested != "auto":
        primary = requested
        reason = f"用户指定 renderer={requested}。"
    elif suffix in {".ppt", ".pptx"}:
        primary = "frontend-slides"
        reason = "输入是PPT/PPTX，优先走转换路径。"
    elif getattr(args, "selected_template", None):
        primary = "beautiful-html-templates"
        reason = f"用户指定 selected_template={args.selected_template}，用选中 Beautiful 模板生成完整 deck。"
    elif args.style_mode == "preview-first":
        primary = "beautiful-html-templates"
        reason = "用户选择 preview-first，优先进入可视化风格探索。"
    elif args.style_mode == "presenter-first" or args.presenter:
        primary = "html-ppt"
        reason = "用户需要演讲者模式，优先走html-ppt。"
    elif language == "zh":
        primary = "guizang"
        reason = "中文内容且未指定风格探索，优先走guizang稳定路径。"
    else:
        primary = "beautiful-html-templates"
        reason = "英文或跨风格内容，先定主题并生成至少5个风格候选，再进入成稿。"

    routes = [
        {
            "id": primary,
            "stage": "produce",
            "purpose": "根据Humanize PPT契约生成主deck或候选预览。",
            "reason": reason,
            "command_file": f"commands/{primary}-agent.md" if primary != "beautiful-html-templates" else "commands/beautiful-agent.md",
            "status": "planned",
        }
    ]
    if args.presenter and primary != "html-ppt":
        routes.append(
            {
                "id": "html-ppt",
                "stage": "complete",
                "purpose": "在最终deck确定后增加演讲者模式和speaker notes。",
                "reason": "presenter=True。",
                "command_file": "commands/html-ppt-agent.md",
                "status": "planned",
            }
        )
    if getattr(args, "presenter_adapter", False):
        routes.append(
            {
                "id": "presenter-adapter",
                "stage": "complete",
                "purpose": "为最终deck生成独立 presenter shell 和逐页 speaker notes。",
                "reason": "presenter_adapter=True。",
                "command_file": "commands/presenter-adapter-agent.md",
                "status": "planned",
            }
        )
    if getattr(args, "export_adapter", False):
        routes.append(
            {
                "id": "export-adapter",
                "stage": "complete",
                "purpose": "为最终deck生成可移植导出包和 PDF 导出脚本。",
                "reason": "export_adapter=True。",
                "command_file": "commands/export-adapter-agent.md",
                "status": "planned",
            }
        )
    routes.append(
        {
            "id": "qa",
            "stage": "control",
            "purpose": "检查契约、路径、人感、AI草稿痕迹和交付完整性。",
            "reason": "所有Humanize PPT运行必须经过QA。",
            "command_file": "commands/qa-agent.md",
            "status": "planned",
        }
    )
    return primary, routes


def resolve_preview_count(language, requested=None):
    if language == "zh":
        return max(1, requested if requested is not None else DEFAULT_ZH_PREVIEW_COUNT)
    baseline = DEFAULT_EN_PREVIEW_COUNT
    return max(baseline, requested if requested is not None else baseline)


def renderer_by_id(registry):
    return {item["id"]: item for item in registry.get("renderers", [])}


def simple_tokens(*values):
    text = " ".join(str(v or "") for v in values).lower()
    tokens = set(re.findall(r"[a-z0-9][a-z0-9-]{1,}|[\u4e00-\u9fff]{2,}", text))
    aliases = {
        "ai": {"agent", "agents", "developer", "tools", "workflow", "product", "launch"},
        "agent": {"ai", "developer", "workflow", "tools"},
        "ppt": {"presentation", "deck", "slides"},
        "工具": {"ai", "tools", "workflow"},
        "产品": {"product", "launch"},
        "发布": {"launch", "product"},
        "分享": {"talk", "presentation", "deck"},
    }
    expanded = set(tokens)
    for token in list(tokens):
        expanded.update(aliases.get(token, set()))
    return expanded


def infer_preview_brief(title, text, language, occasion=None, mood=None):
    inferred_occasion = occasion
    inferred_mood = mood
    lower = text.lower()
    if not inferred_occasion:
        if any(k in lower for k in ["ai", "agent", "skill", "工具", "模型", "工作流"]):
            inferred_occasion = "AI workflow product demo, developer tools, creator presentation"
        else:
            inferred_occasion = "research synthesis, product narrative, presentation"
    if not inferred_mood:
        inferred_mood = "confident editorial modern design-led practical" if language == "zh" else "confident editorial modern design-led"
    return {
        "title": title,
        "occasion": inferred_occasion,
        "mood": inferred_mood,
    }


def template_search_text(template):
    fields = [
        template.get("slug"),
        template.get("name"),
        template.get("tagline"),
        template.get("best_for"),
        template.get("avoid_for"),
        template.get("formality"),
        template.get("density"),
        template.get("scheme"),
        " ".join(template.get("mood", [])),
        " ".join(template.get("occasion", [])),
        " ".join(template.get("tone", [])),
    ]
    return " ".join(str(x or "") for x in fields)


def score_template(template, title, text, occasion, mood):
    wanted = simple_tokens(title, text, occasion, mood)
    mood_tokens = simple_tokens(" ".join(template.get("mood", [])), " ".join(template.get("tone", [])))
    occasion_tokens = simple_tokens(" ".join(template.get("occasion", [])), template.get("best_for", ""))
    all_tokens = simple_tokens(template_search_text(template))
    score = 0
    score += 5 * len(wanted & mood_tokens)
    score += 3 * len(wanted & occasion_tokens)
    score += len(wanted & all_tokens)
    if template.get("density") in {"medium", "high"}:
        score += 2
    if template.get("formality") in {"medium", "medium-high", "high"}:
        score += 1
    return score


def select_beautiful_templates(repo_path, title, text, language, occasion=None, mood=None, count=3):
    repo = Path(repo_path).expanduser()
    index_path = repo / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    brief = infer_preview_brief(title, text, language, occasion, mood)
    scored = []
    for template in index.get("templates", []):
        slug = template.get("slug")
        if not slug or not (repo / "templates" / slug / "template.html").exists():
            continue
        score = score_template(template, title, text, brief["occasion"], brief["mood"])
        scored.append((score, template))
    scored.sort(key=lambda item: (-item[0], item[1].get("slug", "")))

    selected = []
    seen_schemes = set()
    for score, template in scored:
        if len(selected) >= count:
            break
        scheme = template.get("scheme")
        if len(selected) < 2 or scheme not in seen_schemes or len(scored) <= count:
            selected.append((score, template))
            seen_schemes.add(scheme)
    for score, template in scored:
        if len(selected) >= count:
            break
        if template.get("slug") not in {item[1].get("slug") for item in selected}:
            selected.append((score, template))

    results = []
    for score, template in selected[:count]:
        reason = f"匹配 occasion=`{brief['occasion']}`，mood=`{brief['mood']}`；{template.get('tagline', template.get('best_for', ''))}"
        results.append(
            {
                "slug": template["slug"],
                "name": template.get("name", template["slug"]),
                "tagline": template.get("tagline", ""),
                "score": score,
                "reason": reason,
                "mood": template.get("mood", []),
                "tone": template.get("tone", []),
                "scheme": template.get("scheme"),
                "density": template.get("density"),
                "slide_count": template.get("slide_count"),
            }
        )
    return results


def find_beautiful_repo(value=None, auto_clone=True):
    if value:
        path = Path(value).expanduser()
        return path if (path / "index.json").exists() else None
    candidates = [
        Path.home() / ".agents/skills/beautiful-html-templates",
        Path.home() / ".hermes/skills/beautiful-html-templates",
        Path.home() / ".cache/humanize-ppt/beautiful-html-templates",
        Path("/tmp/beautiful-html-templates"),
    ]
    for candidate in candidates:
        if (candidate / "index.json").exists():
            return candidate
    if auto_clone:
        cache = Path.home() / ".cache/humanize-ppt/beautiful-html-templates"
        cache.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", BEAUTIFUL_REPO_URL, str(cache)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return None
        if (cache / "index.json").exists():
            return cache
    return None


def title_html(title):
    raw = " ".join(title.split())
    if len(raw) > 18 and not re.search(r"\s", raw):
        parts = [x for x in re.split(r"([，、：:—-])", raw) if x]
        lines, current = [], ""
        for part in parts:
            if len(current + part) > 14 and current:
                lines.append(current.strip("，、：:—- "))
                current = part
            else:
                current += part
        if current:
            lines.append(current.strip("，、：:—- "))
    else:
        words = raw.split()
        if len(words) > 4:
            mid = max(2, len(words) // 2)
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        else:
            lines = [raw]
    return "<br />".join(html.escape(x) for x in lines if x) or html.escape(title)


def first_cover_section(document):
    match = re.search(r"<section\b[\s\S]*?</section>", document, flags=re.IGNORECASE)
    return match.group(0) if match else ""


def customize_cover_section(section, title, subtitle, kicker):
    if not section:
        return f"<section class=\"slide s-cover\"><h1>{title_html(title)}</h1><p>{html.escape(subtitle)}</p></section>"
    updated = re.sub(
        r"(<h1\b[^>]*>)[\s\S]*?(</h1>)",
        lambda m: m.group(1) + title_html(title) + m.group(2),
        section,
        count=1,
        flags=re.IGNORECASE,
    )
    subtitle_html = html.escape(subtitle)
    if re.search(r"<p\b", updated, flags=re.IGNORECASE):
        updated = re.sub(
            r"(<p\b[^>]*>)[\s\S]*?(</p>)",
            lambda m: m.group(1) + subtitle_html + m.group(2),
            updated,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        updated = re.sub(r"(</h1>)", r"\1\n<p>" + subtitle_html + "</p>", updated, count=1, flags=re.IGNORECASE)
    updated = re.sub(
        r"(<div\b[^>]*class=[\"'][^\"']*(?:kicker|eyebrow|label)[^\"']*[\"'][^>]*>)[\s\S]*?(</div>)",
        lambda m: m.group(1) + html.escape(kicker) + m.group(2),
        updated,
        count=1,
        flags=re.IGNORECASE,
    )
    updated = re.sub(r"01\s*/\s*\d+", "01 / 01", updated, count=1)
    return updated


def keep_first_section_only(document, section):
    if re.search(r"<deck-stage\b", document, flags=re.IGNORECASE):
        return re.sub(
            r"(<deck-stage\b[^>]*>)[\s\S]*?(</deck-stage>)",
            lambda m: m.group(1) + "\n" + section + "\n" + m.group(2),
            document,
            count=1,
            flags=re.IGNORECASE,
        )
    if re.search(r"<div\b[^>]*id=[\"']deck[\"']", document, flags=re.IGNORECASE):
        return re.sub(
            r"(<div\b[^>]*id=[\"']deck[\"'][^>]*>)[\s\S]*?(</div>)",
            lambda m: m.group(1) + "\n" + section + "\n" + m.group(2),
            document,
            count=1,
            flags=re.IGNORECASE,
        )
    return re.sub(r"<body\b([^>]*)>[\s\S]*?</body>", lambda m: f"<body{m.group(1)}>\n{section}\n</body>", document, count=1, flags=re.IGNORECASE)


def copy_preview_assets(repo, template_dir, preview_dir):
    for src in template_dir.iterdir():
        if src.name == "template.html":
            continue
        dst = preview_dir / src.name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dst)
    runtime = repo / "runtime" / "deck-stage.js"
    if runtime.exists() and not (preview_dir / "deck-stage.js").exists():
        shutil.copy2(runtime, preview_dir / "deck-stage.js")


def write_beautiful_gallery(previews_dir, previews):
    cards = []
    for item in previews:
        rel = Path(item["path"]).relative_to(previews_dir)
        cards.append(
            f"""<article><h2>{html.escape(item['name'])}</h2><p>{html.escape(item['reason'])}</p><iframe src=\"{html.escape(str(rel))}\"></iframe></article>"""
        )
    doc = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Beautiful Preview Gallery</title><style>body{{margin:0;background:#111;color:#f7f1e8;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}}main{{padding:32px;display:grid;gap:28px}}article{{border:1px solid rgba(255,255,255,.18);border-radius:18px;padding:20px;background:#181818}}h1{{font-size:40px}}h2{{margin:.2em 0}}p{{color:#cfc7b8}}iframe{{width:100%;aspect-ratio:16/9;border:0;border-radius:12px;background:#000}}</style></head><body><main><h1>Humanize PPT · Beautiful Preview-First</h1>{''.join(cards)}</main></body></html>"""
    gallery = previews_dir / "index.html"
    gallery.write_text(doc, encoding="utf-8")
    return gallery


def write_beautiful_previews(out, title, text, plan, repo_path, language, occasion=None, mood=None, count=3):
    repo = Path(repo_path).expanduser() if repo_path else None
    if not repo or not (repo / "index.json").exists():
        return {
            "status": "missing-library",
            "message": "beautiful-html-templates index.json not found. Pass --beautiful-repo or allow auto clone.",
            "previews": [],
        }
    target = out / "outputs" / "beautiful"
    previews_dir = target / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)
    selected = select_beautiful_templates(repo, title, text, language, occasion, mood, count=count)
    subtitle = plan[0].get("message") if plan else first_sentence(text, fallback="Humanize PPT preview")
    previews = []
    for idx, item in enumerate(selected, 1):
        slug = item["slug"]
        template_dir = repo / "templates" / slug
        preview_dir = previews_dir / f"{idx:02d}-{slug}"
        preview_dir.mkdir(parents=True, exist_ok=True)
        copy_preview_assets(repo, template_dir, preview_dir)
        document = (template_dir / "template.html").read_text(encoding="utf-8", errors="replace")
        section = customize_cover_section(
            first_cover_section(document),
            title=title,
            subtitle=subtitle,
            kicker="Humanize PPT · Preview-First",
        )
        preview_doc = keep_first_section_only(document, section)
        preview_doc = re.sub(r"<title>[\s\S]*?</title>", f"<title>{html.escape(title)} · {html.escape(item['name'])}</title>", preview_doc, count=1, flags=re.IGNORECASE)
        preview_path = preview_dir / "index.html"
        preview_path.write_text(preview_doc, encoding="utf-8")
        previews.append({**item, "path": str(preview_path)})
    gallery = write_beautiful_gallery(previews_dir, previews)
    manifest = {
        "version": VERSION,
        "generated_at": now_iso(),
        "repo": str(repo),
        "title": title,
        "language": language,
        "occasion": occasion,
        "mood": mood,
        "preview_count": len(previews),
        "requested_preview_count": count,
        "gallery": str(gallery),
        "previews": previews,
    }
    (target / "preview_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# Beautiful Render Report", "", "- status: rendered", f"- repo: {repo}", f"- gallery: {gallery}", "", "## Candidates"]
    report.extend([f"- {i}. {item['name']} (`{item['slug']}`): {item['path']}" for i, item in enumerate(previews, 1)])
    (target / "render_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"status": "rendered", "gallery": str(gallery), "previews": previews, "manifest": str(target / "preview_manifest.json"), "report": str(target / "render_report.md")}


def beautiful_slide_section(slide, idx, total, deck_title):
    title = slide.get("title") or deck_title
    message = slide.get("message") or title
    bullets = [x for x in slide.get("visible_content", []) if x and x != message]
    role = slide.get("role", "slide")
    intent = slide.get("speaker_intent", "")
    if idx == 1:
        return f"""<section class=\"slide s-cover humanize-slide humanize-cover\">
  <div class=\"kicker\">Humanize PPT · Selected Template Full Deck</div>
  <h1>{title_html(deck_title)}</h1>
  <p>{html.escape(message)}</p>
  <div class=\"pagenum\">{idx:02d} / {total:02d}</div>
</section>"""
    bullet_html = "".join(f"<li>{html.escape(item)}</li>" for item in bullets[:4])
    if not bullet_html:
        bullet_html = f"<li>{html.escape(message)}</li>"
    return f"""<section class=\"slide humanize-slide\">
  <div class=\"kicker\">{html.escape(role).upper()} · {idx:02d} / {total:02d}</div>
  <h2>{html.escape(title)}</h2>
  <p>{html.escape(message)}</p>
  <ul>{bullet_html}</ul>
  <div class=\"speaker-note\">Speaker intent: {html.escape(intent)}</div>
  <div class=\"pagenum\">{idx:02d} / {total:02d}</div>
</section>"""


def inject_deck_sections(document, sections):
    joined = "\n".join(sections)
    if re.search(r"<deck-stage\b", document, flags=re.IGNORECASE):
        return re.sub(
            r"(<deck-stage\b[^>]*>)[\s\S]*?(</deck-stage>)",
            lambda m: m.group(1) + "\n" + joined + "\n" + m.group(2),
            document,
            count=1,
            flags=re.IGNORECASE,
        )
    if re.search(r"<div\b[^>]*id=[\"']deck[\"']", document, flags=re.IGNORECASE):
        return re.sub(
            r"(<div\b[^>]*id=[\"']deck[\"'][^>]*>)[\s\S]*?(</div>)",
            lambda m: m.group(1) + "\n" + joined + "\n" + m.group(2),
            document,
            count=1,
            flags=re.IGNORECASE,
        )
    return re.sub(r"<body\b([^>]*)>[\s\S]*?</body>", lambda m: f"<body{m.group(1)}>\n{joined}\n</body>", document, count=1, flags=re.IGNORECASE)


def add_selected_deck_controls(document):
    controls = """<script>
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  let index = 0;
  function show(next) {
    index = Math.max(0, Math.min(slides.length - 1, next));
    slides.forEach((slide, i) => {
      slide.style.display = i === index ? '' : 'none';
      slide.setAttribute('aria-hidden', i === index ? 'false' : 'true');
    });
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === ' ') show(index + 1);
    if (event.key === 'ArrowLeft') show(index - 1);
  });
  show(0);
})();
</script>"""
    if "querySelectorAll('.slide')" in document:
        return document
    return re.sub(r"</body>", controls + "\n</body>", document, count=1, flags=re.IGNORECASE)


def write_beautiful_selected_deck(out, title, plan, repo_path, selected_template):
    repo = Path(repo_path).expanduser() if repo_path else None
    if not repo or not (repo / "index.json").exists():
        return {
            "status": "missing-library",
            "message": "beautiful-html-templates index.json not found. Pass --beautiful-repo or allow auto clone.",
        }
    template_dir = repo / "templates" / selected_template
    template_path = template_dir / "template.html"
    if not template_path.exists():
        return {
            "status": "missing-template",
            "message": f"beautiful-html-templates template not found: {selected_template}",
        }

    target = out / "outputs" / "beautiful"
    selected_dir = target / "selected"
    selected_dir.mkdir(parents=True, exist_ok=True)
    copy_preview_assets(repo, template_dir, selected_dir)

    safe_plan = plan or [{"title": title, "message": title, "visible_content": [title], "role": "hook", "speaker_intent": "Introduce the deck."}]
    total = len(safe_plan)
    sections = [beautiful_slide_section(slide, idx, total, title) for idx, slide in enumerate(safe_plan, 1)]
    document = template_path.read_text(encoding="utf-8", errors="replace")
    deck_doc = inject_deck_sections(document, sections)
    deck_doc = add_selected_deck_controls(deck_doc)
    deck_doc = re.sub(r"<title>[\s\S]*?</title>", f"<title>{html.escape(title)} · {html.escape(selected_template)}</title>", deck_doc, count=1, flags=re.IGNORECASE)

    deck_path = selected_dir / "index.html"
    deck_path.write_text(deck_doc, encoding="utf-8")
    manifest = {
        "version": VERSION,
        "generated_at": now_iso(),
        "repo": str(repo),
        "title": title,
        "selected_template": selected_template,
        "deck": str(deck_path),
        "slide_count": total,
    }
    (target / "selected_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Beautiful Render Report",
        "",
        "- status: rendered",
        "- mode: selected-template-full-deck",
        f"- template: {selected_template}",
        f"- output: {deck_path}",
        f"- slides: {total}",
    ]
    (target / "render_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"status": "rendered", "template": selected_template, "deck": str(deck_path), "manifest": str(target / "selected_manifest.json"), "report": str(target / "render_report.md")}


def speaker_script(slide):
    parts = [slide.get("speaker_intent", ""), slide.get("message", "")]
    parts.extend(slide.get("visible_content", [])[:3])
    return "\n".join(str(x) for x in parts if x)


def relative_href(from_dir, target):
    return os.path.relpath(Path(target).resolve(), Path(from_dir).resolve()).replace(os.sep, "/")


def write_presenter_adapter(out, title, plan, deck_path):
    deck = Path(deck_path).expanduser() if deck_path else None
    if not deck or not deck.exists():
        return {"status": "missing-deck", "message": f"deck not found: {deck_path}"}

    target = out / "outputs" / "presenter"
    target.mkdir(parents=True, exist_ok=True)
    deck_href = relative_href(target, deck)
    safe_plan = plan or [{"slide_id": "S01", "title": title, "message": title, "speaker_intent": "Introduce the deck."}]
    notes = [
        {
            "slide_id": slide.get("slide_id", f"S{idx:02d}"),
            "title": slide.get("title") or title,
            "message": slide.get("message") or "",
            "script": speaker_script(slide),
        }
        for idx, slide in enumerate(safe_plan, 1)
    ]
    notes_json = json.dumps(notes, ensure_ascii=False)
    doc = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{html.escape(title)} · Presenter</title><style>
body{{margin:0;background:#0f1117;color:#f5efe3;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;height:100vh;overflow:hidden}}
main{{display:grid;grid-template-columns:minmax(0,2fr) minmax(340px,1fr);height:100vh}}
.stage{{background:#050507;display:grid;place-items:center;padding:18px}}
iframe{{width:100%;aspect-ratio:16/9;border:0;border-radius:16px;background:#000;box-shadow:0 20px 80px rgba(0,0,0,.45)}}
aside{{border-left:1px solid rgba(255,255,255,.12);padding:22px;display:grid;grid-template-rows:auto auto 1fr auto;gap:16px;background:#171923}}
.kicker{{letter-spacing:.12em;color:#e5b65b;font-size:12px;text-transform:uppercase}}h1{{margin:.1em 0;font-size:28px}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.card{{border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:14px;background:rgba(255,255,255,.05)}}.label{{font-size:11px;color:#9aa3b2;letter-spacing:.12em}}#script{{white-space:pre-wrap;font-size:20px;line-height:1.55;overflow:auto}}button{{border:0;border-radius:12px;padding:12px 16px;background:#e5b65b;color:#111;font-weight:700}}.nav{{display:flex;gap:10px;align-items:center}}
</style></head><body><main><section class=\"stage\"><iframe id=\"deck\" src=\"{html.escape(deck_href)}?slide=1\"></iframe></section><aside><div><div class=\"kicker\">Humanize PPT · Presenter Adapter</div><h1>{html.escape(title)}</h1></div><div class=\"cards\"><div class=\"card\"><div class=\"label\">CURRENT</div><strong id=\"current\"></strong></div><div class=\"card\"><div class=\"label\">NEXT</div><strong id=\"next\"></strong></div></div><div class=\"card\"><div class=\"label\">SCRIPT</div><div id=\"script\"></div></div><div class=\"nav\"><button id=\"prev\">← Prev</button><button id=\"nextBtn\">Next →</button><span id=\"counter\"></span></div></aside></main><script>
const notes = {notes_json};
let idx = 0;
const deck = document.getElementById('deck');
const deckBase = deck.getAttribute('src').replace(/\\?.*$/, '');
function deckUrl(index) {{
  return `${{deckBase}}?slide=${{index + 1}}`;
}}
function syncDeck() {{
  if(deck.contentWindow) {{
    deck.contentWindow.postMessage({{type:'presenter-goto', index:idx}}, '*');
    deck.contentWindow.postMessage({{type:'preview-goto', idx}}, '*');
  }}
}}
function render() {{
  const item = notes[idx] || notes[0];
  const next = notes[idx + 1];
  document.getElementById('current').textContent = item ? `${{item.slide_id}} · ${{item.title}}` : '';
  document.getElementById('next').textContent = next ? `${{next.slide_id}} · ${{next.title}}` : 'END';
  document.getElementById('script').textContent = item ? item.script : '';
  document.getElementById('counter').textContent = `${{idx + 1}} / ${{notes.length}}`;
  syncDeck();
}}
function go(next) {{
  idx = Math.max(0, Math.min(notes.length - 1, next));
  const target = deckUrl(idx);
  if(!deck.src.endsWith(`slide=${{idx + 1}}`)) deck.src = target;
  render();
}}
document.getElementById('prev').onclick = () => go(idx - 1);
document.getElementById('nextBtn').onclick = () => go(idx + 1);
document.addEventListener('keydown', e => {{ if (e.key === 'ArrowRight') go(idx + 1); if (e.key === 'ArrowLeft') go(idx - 1); }});
deck.addEventListener('load', syncDeck);
render();
</script></body></html>"""
    presenter = target / "index.html"
    presenter.write_text(doc, encoding="utf-8")
    manifest = {
        "version": VERSION,
        "generated_at": now_iso(),
        "title": title,
        "deck": str(deck),
        "presenter": str(presenter),
        "slide_count": len(safe_plan),
        "notes": notes,
    }
    (target / "presenter_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (target / "render_report.md").write_text(f"# Presenter Adapter Report\n\n- status: rendered\n- deck: {deck}\n- presenter: {presenter}\n- slides: {len(safe_plan)}\n", encoding="utf-8")
    return {"status": "rendered", "presenter": str(presenter), "manifest": str(target / "presenter_manifest.json"), "report": str(target / "render_report.md")}


def export_script_text():
    return """#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HTML="${1:-$HERE/package/index.html}"
OUT="${2:-$HERE/deck.pdf}"
python3 - "$HTML" "$OUT" <<'PY'
import asyncio, sys
from pathlib import Path

html_path = Path(sys.argv[1]).resolve()
out_path = Path(sys.argv[2]).resolve()

async def main():
    try:
        from playwright.async_api import async_playwright
    except Exception:
        raise SystemExit("Missing playwright. Run: python3 -m pip install playwright && python3 -m playwright install chromium")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.pdf(path=str(out_path), width="1920px", height="1080px", print_background=True)
        await browser.close()

asyncio.run(main())
print(out_path)
PY
"""


def write_export_adapter(out, title, deck_path, slide_count):
    deck = Path(deck_path).expanduser() if deck_path else None
    if not deck or not deck.exists():
        return {"status": "missing-deck", "message": f"deck not found: {deck_path}"}

    target = out / "outputs" / "export"
    package = target / "package"
    if package.exists():
        shutil.rmtree(package)
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(deck.parent, package)

    script = target / "export_pdf.sh"
    script.write_text(export_script_text(), encoding="utf-8")
    script.chmod(0o755)
    readme = target / "README.md"
    readme.write_text(
        f"""# Export Package

- Source deck: `{deck}`
- Portable HTML: `outputs/export/package/index.html`
- PDF command: `bash outputs/export/export_pdf.sh outputs/export/package/index.html outputs/export/deck.pdf`

Notes:
- PDF export uses Playwright Chromium.
- Animations and keyboard navigation become static PDF pages.
""",
        encoding="utf-8",
    )
    manifest = {
        "version": VERSION,
        "generated_at": now_iso(),
        "title": title,
        "deck": str(deck),
        "package": str(package),
        "html": str(package / "index.html"),
        "export_script": str(script),
        "slide_count": slide_count,
    }
    (target / "export_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (target / "render_report.md").write_text(f"# Export Adapter Report\n\n- status: packaged\n- package: {package}\n- script: {script}\n- slides: {slide_count}\n", encoding="utf-8")
    return {"status": "packaged", "package": str(package), "manifest": str(target / "export_manifest.json"), "script": str(script), "report": str(target / "render_report.md")}


def write_router_plan(out, title, source_path, primary, routes, registry):
    known = renderer_by_id(registry)
    enriched = []
    for route in routes:
        info = known.get(route["id"], {})
        merged = dict(route)
        merged.update(
            {
                "display_name": info.get("display_name", route["id"]),
                "skill_name": info.get("skill_name", route["id"]),
                "expected_inputs": info.get("inputs", []),
                "expected_outputs": info.get("outputs", []),
            }
        )
        enriched.append(merged)
    plan = {
        "version": VERSION,
        "generated_at": now_iso(),
        "title": title,
        "source": str(source_path),
        "primary_renderer": primary,
        "routes": enriched,
    }
    (out / "router_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def command_text(route, out):
    rid = route["id"]
    output_map = {
        "beautiful-html-templates": "beautiful",
        "presenter-adapter": "presenter",
        "export-adapter": "export",
    }
    output_dir = f"outputs/{output_map.get(rid, rid)}"
    if rid == "qa":
        output_dir = "outputs/qa"
    read_list = "\n".join(f"- {name}" for name in route.get("expected_inputs", [])) or "- deck_brief.md\n- slide_plan.json"
    return f"""# {route.get('display_name', rid)} Command

You are the {route.get('display_name', rid)} specialist agent.
Load skill: {route.get('skill_name', rid)}
Input directory: {out}

Read:
{read_list}

Task:
{route['purpose']}

Write outputs to:
{out / output_dir}

Do not:
- rewrite the AST goal
- consume raw source unless this command explicitly says so
- change another agent's outputs
- invent missing assets without marking them as generated or placeholder
- put model thinking process or draft notes on visible slides

Return:
- output paths
- renderer/template/style decisions
- known issues
- verification result
"""


def write_commands(out, router_plan):
    commands = out / "commands"
    commands.mkdir(exist_ok=True)
    for route in router_plan["routes"]:
        name = route["command_file"].split("/")[-1]
        (commands / name).write_text(command_text(route, out), encoding="utf-8")


# v0.6.4: Humanize PPT no longer imitates the Guizang renderer.
# It stops at the production brief; guizang-ppt-skill renders natively.
# See references/guizang-production-brief-orchestrator.md for the boundary contract.


# ---------------------------------------------------------------------------
# QA failure mode catalog (Lane C)
# ---------------------------------------------------------------------------
# v0.6.5: install self-check for downstream skills.
# ---------------------------------------------------------------------------

DOWNSTREAM_SKILL_PATHS = {
    "guizang-ppt-skill": [
        Path.home() / ".agents" / "skills" / "guizang-ppt-skill" / "SKILL.md",
        Path.home() / ".hermes" / "skills" / "guizang-ppt-skill" / "SKILL.md",
    ],
    "frontend-slides": [
        Path.home() / ".agents" / "skills" / "frontend-slides" / "SKILL.md",
        Path.home() / ".hermes" / "skills" / "frontend-slides" / "SKILL.md",
    ],
    "beautiful-html-templates": [
        Path.home() / ".agents" / "skills" / "beautiful-html-templates" / "SKILL.md",
        Path.home() / ".hermes" / "skills" / "beautiful-html-templates" / "SKILL.md",
    ],
}


def check_downstream_install(skill_name, skip=False):
    """Return (installed: bool, path: Path|None). If not installed and not
    skipped, print a stderr warning with the install command. Never fatal —
    the brief is still written and the next agent is told to install.
    """
    paths = DOWNSTREAM_SKILL_PATHS.get(skill_name, [])
    for p in paths:
        if p.exists():
            return True, p
    if not skip:
        sys.stderr.write(
            f"\n[humanize-ppt v0.6.5] WARNING: {skill_name} not detected at any known path:\n"
            f"  - " + "\n  - ".join(str(p) for p in paths) + "\n"
            f"  The brief still ships, but the next agent must install {skill_name} before rendering.\n"
            f"  Install: see the skill's GitHub README, or use the agent's skill install command.\n"
            f"  To suppress this warning, pass --skip-install-check.\n\n"
        )
    return False, None


# ---------------------------------------------------------------------------
# Single source of truth for the conversational QA loop. The human-readable
# reference is references/qa-failure-modes.md; ids must match exactly.

REGISTERED_SWISS_LAYOUTS = {f"S{n:02d}" for n in range(1, 23)}  # S01..S22

FAILURE_MODES = {
    "placeholder-residue": {
        "scope": ["guizang"],
        "severity_default": "fail",
        "description": "Template placeholders like [必填] or SLIDES_HERE leaked into the rendered HTML.",
        "check": "check_placeholder_residue",
    },
    "low-power-default": {
        "scope": ["guizang"],
        "severity_default": "fail",
        "description": "body.low-power is active by default, suppressing animation.",
        "check": "check_low_power_default",
    },
    "webgl-canvas-missing": {
        "scope": ["guizang-style-a"],
        "severity_default": "fail",
        "description": "Dual WebGL canvas (canvas#bg-dark and canvas#bg-light) is absent.",
        "check": "check_webgl_canvas_missing",
    },
    "data-anim-thin": {
        "scope": ["guizang-style-a"],
        "severity_default": "fail",
        "description": "data-anim / data-animate markers are too few to drive a watchable deck.",
        "check": "check_data_anim_thin",
    },
    "swiss-sxx-count-mismatch": {
        "scope": ["guizang-style-b"],
        "severity_default": "fail",
        "description": "data-layout=Sxx marker count does not match slide_plan.json slide count.",
        "check": "check_swiss_sxx_count_mismatch",
    },
    "swiss-sxx-invented-id": {
        "scope": ["guizang-style-b"],
        "severity_default": "fail",
        "description": "A data-layout=Sxx value is not in the registered S01..S22 set.",
        "check": "check_swiss_sxx_invented_id",
    },
    "swiss-low-diversity": {
        "scope": ["guizang-style-b"],
        "severity_default": "warn",
        "description": "Fewer than 60% unique Sxx values for the deck length.",
        "check": "check_swiss_low_diversity",
    },
}


def _finding(check_id, severity, evidence, pages=None):
    return {
        "id": check_id,
        "severity": severity,
        "evidence": evidence,
        "pages": pages or [],
    }


def check_placeholder_residue(html, plan, ctx):
    findings = []
    if "[必填]" in html:
        findings.append(_finding(
            "placeholder-residue", "fail",
            "Rendered HTML still contains [必填] template residue.",
        ))
    if "SLIDES_HERE" in html:
        findings.append(_finding(
            "placeholder-residue", "fail",
            "Rendered HTML still contains SLIDES_HERE marker.",
        ))
    return findings


def check_low_power_default(html, plan, ctx):
    findings = []
    body_match = re.search(r"<body\b[^>]*class=[\"']([^\"']*)[\"']", html, flags=re.IGNORECASE)
    if body_match and "low-power" in (body_match.group(1) or "").split():
        findings.append(_finding(
            "low-power-default", "fail",
            f"body has class='{body_match.group(1)}'; low-power must not be a default.",
        ))
    return findings


def check_webgl_canvas_missing(html, plan, ctx):
    findings = []
    missing = []
    if 'id="bg-dark"' not in html and "id='bg-dark'" not in html:
        missing.append("canvas#bg-dark")
    if 'id="bg-light"' not in html and "id='bg-light'" not in html:
        missing.append("canvas#bg-light")
    if missing:
        findings.append(_finding(
            "webgl-canvas-missing", "fail",
            f"Style A requires {', '.join(missing)} for the WebGL hero background.",
        ))
    return findings


def check_data_anim_thin(html, plan, ctx):
    findings = []
    count = len(re.findall(r"\bdata-anim(?:ate)?\b", html))
    if count < 3:
        findings.append(_finding(
            "data-anim-thin", "fail",
            f"Only {count} data-anim/data-animate markers. Need at least 3 (Ink Classic has 86).",
        ))
    elif count < 10:
        findings.append(_finding(
            "data-anim-thin", "warn",
            f"Only {count} data-anim markers. Soft warning; Ink Classic has 86.",
        ))
    return findings


def check_swiss_sxx_count_mismatch(html, plan, ctx):
    findings = []
    markers = re.findall(r'data-layout=[\"\'](S\d{2})[\"\']', html)
    expected = len(plan)
    if len(markers) != expected:
        findings.append(_finding(
            "swiss-sxx-count-mismatch", "fail",
            f"Found {len(markers)} data-layout=Sxx markers; slide_plan has {expected} slides.",
        ))
    return findings


def check_swiss_sxx_invented_id(html, plan, ctx):
    findings = []
    markers = re.findall(r'data-layout=[\"\'](S\d{2})[\"\']', html)
    invented = sorted({m for m in markers if m not in REGISTERED_SWISS_LAYOUTS})
    if invented:
        findings.append(_finding(
            "swiss-sxx-invented-id", "fail",
            f"Invented non-registered Sxx values: {', '.join(invented)}. Registered set is S01..S22.",
            pages=[],
        ))
    return findings


def check_swiss_low_diversity(html, plan, ctx):
    findings = []
    markers = re.findall(r'data-layout=[\"\'](S\d{2})[\"\']', html)
    if not markers:
        return findings
    unique = len(set(markers))
    expected = len(plan)
    floor = max(3, int(expected * 0.6))
    if unique < 3:
        findings.append(_finding(
            "swiss-low-diversity", "fail",
            f"Only {unique} unique Sxx values; minimum is 3.",
        ))
    elif unique < floor:
        findings.append(_finding(
            "swiss-low-diversity", "warn",
            f"Only {unique} unique Sxx values; soft floor is {floor} (60% of {expected} slides).",
        ))
    return findings


_CHECK_FUNCTIONS = {
    "check_placeholder_residue": check_placeholder_residue,
    "check_low_power_default": check_low_power_default,
    "check_webgl_canvas_missing": check_webgl_canvas_missing,
    "check_data_anim_thin": check_data_anim_thin,
    "check_swiss_sxx_count_mismatch": check_swiss_sxx_count_mismatch,
    "check_swiss_sxx_invented_id": check_swiss_sxx_invented_id,
    "check_swiss_low_diversity": check_swiss_low_diversity,
}


def failure_modes_for(renderer, style=None):
    """Return the failure modes that apply to (renderer, style)."""
    target = renderer if not style else f"{renderer}-style-{style.lower()}"
    out = {}
    for mode_id, meta in FAILURE_MODES.items():
        if target in meta["scope"] or renderer in meta["scope"]:
            out[mode_id] = meta
    return out


def run_checks(html, plan, modes):
    """Run each mode's check and return a list of findings."""
    ctx = {"html_len": len(html), "slide_count": len(plan)}
    findings = []
    for mode_id, meta in modes.items():
        fn = _CHECK_FUNCTIONS.get(meta["check"])
        if not fn:
            continue
        for f in fn(html, plan, ctx):
            findings.append(f)
    return findings


# ---------------------------------------------------------------------------
# QA iteration files
# ---------------------------------------------------------------------------


def _qa_dir(out):
    d = out / "outputs" / "qa"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_iteration(out):
    p = _qa_dir(out) / "qa_iteration.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def _write_iteration(out, data):
    p = _qa_dir(out) / "qa_iteration.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_qa_report(out, iteration, findings, status, max_iterations):
    qa = _qa_dir(out)
    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    warn_count = sum(1 for f in findings if f["severity"] == "warn")
    lines = [
        "# QA Report",
        "",
        f"- iteration: {iteration} / {max_iterations}",
        f"- status: {status}",
        f"- fail: {fail_count}",
        f"- warn: {warn_count}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No findings. Deck is clean.")
    else:
        for f in findings:
            lines.append(f"### `{f['id']}` — {f['severity']}")
            lines.append("")
            lines.append(f"- evidence: {f['evidence']}")
            if f.get("pages"):
                lines.append(f"- pages: {', '.join(f['pages'])}")
            lines.append("")
    (qa / "qa_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_fix_prompt(out, iteration, unresolved, rendered_path, style):
    qa = _qa_dir(out)
    if not unresolved:
        (qa / "fix_prompt.md").write_text(
            "# Fix Prompt\n\nNo open findings. Convergence reached.\n",
            encoding="utf-8",
        )
        return
    lines = [
        "# Fix Prompt",
        "",
        f"> Round {iteration}. Apply the following to the rendered HTML",
        f"> at `{rendered_path}` via the downstream skill's native re-render.",
        f"> Do not post-process in Humanize.",
        "",
        "## Style",
        f"- renderer: guizang",
        f"- style: {style}",
        "",
        "## Fix instructions (one per finding)",
        "",
    ]
    fix_specs = {
        "placeholder-residue": "Substitute all [必填] placeholders and remove the <!-- SLIDES_HERE --> marker. The downstream skill's own substitution pass must run end-to-end.",
        "low-power-default": "Remove `low-power` from the body class. Animation must play on first load.",
        "webgl-canvas-missing": "Add both `canvas#bg-dark` and `canvas#bg-light` so the Style A WebGL hero background can render.",
        "data-anim-thin": "Add more `data-anim` / `data-animate` markers across non-cover pages. Aim for 10+ (Ink Classic has 86).",
        "swiss-sxx-count-mismatch": "Make the number of `data-layout=\"Sxx\"` markers equal to the slide count in slide_plan.json. Re-emit from the downstream skill.",
        "swiss-sxx-invented-id": "Replace the invented Sxx values with registered S01..S22 layout IDs from `references/layouts-swiss.md`.",
        "swiss-low-diversity": "Diversify the Swiss layouts. Pick a different registered Sxx per slide where possible. Floor is 60% unique values.",
    }
    for f in unresolved:
        spec = fix_specs.get(f["id"], f["evidence"])
        lines.append(f"### `{f['id']}` ({f['severity']})")
        lines.append("")
        lines.append(f"- evidence: {f['evidence']}")
        if f.get("pages"):
            lines.append(f"- pages: {', '.join(f['pages'])}")
        lines.append(f"- fix: {spec}")
        lines.append("")
    (qa / "fix_prompt.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_qa_mode(args):
    """Post-render QA loop. Reads a rendered HTML, scans for failure modes,
    writes qa_report.md and fix_prompt.md, tracks iteration.
    """
    rendered = Path(args.qa_from).expanduser().resolve()
    if not rendered.exists():
        sys.stderr.write(f"--qa-from path not found: {rendered}\n")
        return 2

    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    renderer = args.renderer if args.renderer != "auto" else "guizang"
    style = (getattr(args, "guizang_style", None) or "A").upper()
    max_iter = max(1, int(getattr(args, "max_qa_iterations", 3) or 3))

    plan_path = out / "slide_plan.json"
    plan = []
    if plan_path.exists():
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except Exception:
            plan = []

    prev = _read_iteration(out)
    iteration = (prev["iteration"] + 1) if prev else 1

    if prev and prev.get("status") == "needs-human":
        # Cap already reached last round. Don't re-loop.
        sys.stderr.write(
            f"qa loop already at needs-human (round {prev['iteration']}). "
            f"Re-render via the downstream skill, then run --qa-from again.\n"
        )
        return 0

    if iteration > max_iter:
        # Should not normally hit here because we set needs-human on the
        # last real round, but guard anyway.
        _write_iteration(out, {
            "iteration": iteration,
            "status": "needs-human",
            "max_iterations": max_iter,
            "renderer": renderer,
            "style": style,
            "unresolved": [],
            "history": (prev or {}).get("history", []),
        })
        sys.stderr.write(f"qa cap reached ({max_iter} rounds). Status: needs-human.\n")
        return 0

    html = rendered.read_text(encoding="utf-8", errors="replace")
    modes = failure_modes_for(renderer, style=style)
    findings = run_checks(html, plan, modes)
    fail_findings = [f for f in findings if f["severity"] == "fail"]
    warn_findings = [f for f in findings if f["severity"] == "warn"]

    resolved = []
    unresolved_failures = list(fail_findings)
    if prev:
        prev_unresolved_ids = {f["id"] for f in prev.get("unresolved", [])}
        resolved = [fid for fid in prev_unresolved_ids if fid not in {f["id"] for f in fail_findings}]
        # If the previous round had un-resolved failures, those carry forward
        # even if the new check doesn't re-trigger them — treat them as
        # still-open.
        carry_over = [f for f in prev.get("unresolved", []) if f["id"] in {f["id"] for f in fail_findings}]
        unresolved_failures = carry_over + [f for f in fail_findings if f not in carry_over]

    converged = not unresolved_failures
    is_last = iteration >= max_iter
    if converged:
        status = "pass"
    elif is_last:
        status = "needs-human"
    else:
        status = "iterate"

    _write_qa_report(out, iteration, findings, status, max_iter)
    _write_fix_prompt(out, iteration, unresolved_failures, rendered, style)

    history = list((prev or {}).get("history", []))
    history.append({
        "iteration": iteration,
        "status": status,
        "fail_count": len(fail_findings),
        "warn_count": len(warn_findings),
        "unresolved_ids": sorted({f["id"] for f in unresolved_failures}),
        "resolved_ids": sorted(resolved),
    })
    _write_iteration(out, {
        "iteration": iteration,
        "status": status,
        "max_iterations": max_iter,
        "renderer": renderer,
        "style": style,
        "unresolved": unresolved_failures,
        "history": history,
    })

    print(json.dumps(
        {
            "iteration": iteration,
            "max_iterations": max_iter,
            "status": status,
            "fail": len(fail_findings),
            "warn": len(warn_findings),
            "qa_report": str(out / "outputs" / "qa" / "qa_report.md"),
            "fix_prompt": str(out / "outputs" / "qa" / "fix_prompt.md"),
            "iteration_file": str(out / "outputs" / "qa" / "qa_iteration.json"),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def write_guizang_production_brief(out, title, plan, source, language, style="A", theme=None, accent=None):
    """Write only the Guizang production brief. No HTML is produced here.

    The next agent must read `guizang-ppt-skill/SKILL.md` and render natively.
    Humanize never opens the Guizang template, never injects sections, and
    never post-processes the rendered HTML.
    """
    style = (style or "A").upper()
    if style not in {"A", "B"}:
        style = "A"

    # v0.6.5: 9 combinations = Style A (5 fixed themes) + Style B (4 accent colors).
    # Style A themes cannot be customized — pick from the 5 presets.
    # Style B accents are single-color overlays on the Swiss template.
    style_a_themes = {
        "ink-classic":      "Ink Classic (墨水经典) — the verified known-good baseline at examples/03-codex-guizang-native-ink-classic/",
        "indigo-porcelain": "Indigo Porcelain (靛蓝瓷) — blue-grey porcelain palette",
        "forest-ink":       "Forest Ink (森林墨) — green-on-cream palette",
        "kraft-paper":      "Kraft Paper (牛皮纸) — warm brown paper palette",
        "dune":             "Dune (沙丘) — sand-and-shadow palette",
    }
    style_b_accents = {
        "ikb":             "Klein Blue (IKB) — International Klein Blue, the most-cited Swiss reference",
        "lemon-yellow":    "Lemon Yellow — high-contrast pop accent on Swiss grid",
        "lemon-green":     "Lemon Green — fresh accent for tech/data topics",
        "safety-orange":   "Safety Orange — warning-construction energy, for tension / call-to-action slides",
    }

    if style == "A":
        theme_key = (theme or "ink-classic").lower()
        if theme_key not in style_a_themes:
            theme_key = "ink-classic"
        style_table = {
            "template": "assets/template.html",
            "layouts": "references/layouts.md",
            "themes": "references/themes.md",
            "theme_preset": theme_key,
            "theme_label": style_a_themes[theme_key],
            "validator": "guizang's own Style A visual QA checklist (see references/guizang-material-qa.md)",
            "lock": "(none — Style A is the flexible track)",
        }
    else:
        accent_key = (accent or "ikb").lower()
        if accent_key not in style_b_accents:
            accent_key = "ikb"
        style_table = {
            "template": "assets/template-swiss.html",
            "layouts": "references/layouts-swiss.md",
            "themes": "references/themes-swiss.md",
            "accent": accent_key,
            "accent_label": style_b_accents[accent_key],
            "validator": "scripts/validate-swiss-deck.mjs",
            "lock": "references/swiss-layout-lock.md",
        }

    inputs_block = "\n".join(
        f"- `{name}`"
        for name in [
            "deck_brief.md",
            "ast_outline.md",
            "slide_plan.json",
            "speaker_intent.md",
            "asset_manifest.md",
            "video_slots.json",
            "style_brief.md",
        ]
    )

    media_lines = []
    for p in plan:
        slide_id = p.get("slide_id", "")
        media = p.get("media") or {}
        image = media.get("image") or {}
        diagram = media.get("diagram") or {}
        video = media.get("video") or {}
        bits = []
        if image.get("needed"):
            bits.append(f"image={image.get('kind', 'unspecified')}")
        if diagram.get("needed"):
            bits.append(f"diagram={diagram.get('kind', 'svg-html')}")
        if video.get("needed"):
            bits.append(f"video={video.get('kind', 'remotion-clip')} ({video.get('duration_s', '?')}s)")
        if not bits:
            bits.append("no media")
        media_lines.append(f"- {slide_id} {p.get('title', '')} — {', '.join(bits)}")

    media_block = "\n".join(media_lines) if media_lines else "- (no slide-level media decisions in this plan)"

    style_a_qa = """\
- no `[必填]` template residue
- no `<!-- SLIDES_HERE -->` marker residue
- `canvas#bg-dark` exists
- `canvas#bg-light` exists
- `body.low-power` is not active by default
- `.slide.hero.light,.slide.hero.dark { background: transparent }` is applied so the WebGL hero canvas is visible
- meaningful `data-anim` / `data-animate` markers are present
- at least 3 `data-anim` occurrences per non-cover page (Ink Classic checkpoint has 86)"""

    style_b_qa = """\
- `scripts/validate-swiss-deck.mjs` exits with code 0
- every slide has a registered `data-layout="Sxx"` marker
- `data-layout` count equals slide count
- at least 6 unique Swiss layouts for a 7-8 page deck (higher for longer decks)
- no invented, non-registered layout IDs
- no inserted SVG/image/video frame clips, overlaps, or hugs the slide edge
- inserted materials do not repeat the slide title"""

    prompt = f"""# Guizang Production Prompt

> Humanize PPT stops here. The next agent must follow
> `~/.agents/skills/guizang-ppt-skill/SKILL.md` end to end.
> Do not reimplement Guizang inside Humanize. Do not import the
> Guizang template into Humanize. Do not post-process the rendered HTML
> with Humanize-owned bridges — Guizang owns its own navigation.

## Deck

- Title: {title}
- Source: {source}
- Language: {language}
- Style: {style}
{('- Theme preset: ' + style_table.get('theme_preset', '') + ' (' + style_table.get('theme_label', '') + ')') if style == 'A' else ''}
{('- Accent color: ' + style_table.get('accent', '') + ' (' + style_table.get('accent_label', '') + ')') if style == 'B' else ''}
- Slides: {len(plan)}

## Style files (use the ones for Style {style})

- template: `{style_table['template']}`
- layouts: `{style_table['layouts']}`
- themes: `{style_table['themes']}`
- lock: {style_table['lock']}
- validator: `{style_table['validator']}`
{("- Apply theme preset: `" + style_table.get('theme_preset', '') + "` from references/themes.md") if style == 'A' else ''}
{("- Apply accent color: `" + style_table.get('accent', '') + "` from references/themes-swiss.md") if style == 'B' else ''}

## Hard rules

- Read `guizang-ppt-skill/SKILL.md` before any rendering. Do not skip it.
- Pick every page's layout from the registered set in
  `{style_table['layouts']}`. Do not invent layout classes.
- Preserve Guizang's animation hooks (`data-anim` / `data-animate`),
  Motion One loading, and the WebGL dual canvas where Style A applies.
- This prompt requires `guizang-ppt-skill` to be installed at
  `~/.agents/skills/guizang-ppt-skill/`. If it is not, the next agent
  must install it before rendering. The brief still ships.
- Run the validator above before reporting complete.
- Do not modify or post-process the rendered HTML in Humanize.
- The HTML that ends up on disk is produced by `guizang-ppt-skill`,
  not by Humanize.

## Inputs already produced by Humanize

{inputs_block}

## Per-page media decisions (Humanize-owned)

{media_block}

## Known-good checkpoint (read-only reference)

- `examples/03-codex-guizang-native-ink-classic/index.html`
  (Style A, Ink Classic, 10 slides, hero WebGL background, 86 `data-anim`
  occurrences). Open it to see the bar for Style A quality.

## Style {style} QA gates (must all pass)

{style_a_qa if style == 'A' else style_b_qa}

## Hand-off

The next agent writes its output to its own convention
(e.g. `outputs/guizang-rendered/index.html`). Do not write to
`outputs/guizang/` — that is reserved for legacy Humanize adapter paths
and is no longer used in v0.6.4.
"""

    (out / "guizang-production-prompt.md").write_text(prompt, encoding="utf-8")
    return {
        "status": "brief-written",
        "prompt": str(out / "guizang-production-prompt.md"),
        "style": style,
        "slides": len(plan),
    }


def write_frontend_slides_production_brief(out, title, plan, source, language):
    """Write only the frontend-slides production brief. No HTML is produced.

    Skeleton: the next agent must follow
    `~/.agents/skills/frontend-slides/SKILL.md` and use its own native
    pipeline (PPTX → HTML conversion, viewport-safe HTML deck, deploy).
    Humanize never opens the frontend-slides template.
    """
    inputs_block = "\n".join(
        f"- `{name}`"
        for name in [
            "deck_brief.md",
            "ast_outline.md",
            "slide_plan.json",
            "speaker_intent.md",
            "asset_manifest.md",
            "video_slots.json",
            "style_brief.md",
        ]
    )

    prompt = f"""# Frontend Slides Production Prompt

> Humanize PPT stops here. The next agent must follow
> `~/.agents/skills/frontend-slides/SKILL.md` end to end.
> Do not reimplement the renderer inside Humanize.

## Deck

- Title: {title}
- Source: {source}
- Language: {language}
- Slides: {len(plan)}

## Hard rules

- Read `frontend-slides/SKILL.md` first. Use its native PPTX→HTML
  conversion, viewport-safe deck, and Vercel deploy path.
- Use the registered layouts / templates that skill ships with. Do not
  invent layout classes.
- Do not post-process the rendered HTML in Humanize. Frontend-slides
  owns its own navigation, presenter shell, and deploy step.

## Inputs already produced by Humanize

{inputs_block}

## Hand-off

The next agent writes its output to its own convention
(e.g. `outputs/frontend-slides-rendered/index.html`).
"""

    (out / "frontend-slides-production-prompt.md").write_text(prompt, encoding="utf-8")
    return {
        "status": "brief-written",
        "prompt": str(out / "frontend-slides-production-prompt.md"),
        "slides": len(plan),
    }


def write_beautiful_html_templates_production_brief(out, title, plan, source, language):
    """Write only the beautiful-html-templates production brief. No HTML produced.

    Skeleton: the next agent must follow
    `~/.agents/skills/beautiful-html-templates/SKILL.md` and use its own
    native template selection + full-deck rendering.
    Humanize never copies templates or injects sections.
    """
    inputs_block = "\n".join(
        f"- `{name}`"
        for name in [
            "deck_brief.md",
            "ast_outline.md",
            "slide_plan.json",
            "speaker_intent.md",
            "asset_manifest.md",
            "video_slots.json",
            "style_brief.md",
        ]
    )

    prompt = f"""# Beautiful HTML Templates Production Prompt

> Humanize PPT stops here. The next agent must follow
> `~/.agents/skills/beautiful-html-templates/SKILL.md` end to end.
> Do not reimplement the renderer inside Humanize.

## Deck

- Title: {title}
- Source: {source}
- Language: {language}
- Slides: {len(plan)}

## Hard rules

- Read `beautiful-html-templates/SKILL.md` first. Use its native
  template selection, preview gallery, and selected-template full-deck
  generation.
- Do not copy templates or inject custom sections into Humanize.
  Beautiful owns the rendered HTML end-to-end.

## Inputs already produced by Humanize

{inputs_block}

## Hand-off

The next agent writes its output to its own convention
(e.g. `outputs/beautiful-rendered/index.html`).
"""

    (out / "beautiful-html-templates-production-prompt.md").write_text(prompt, encoding="utf-8")
    return {
        "status": "brief-written",
        "prompt": str(out / "beautiful-html-templates-production-prompt.md"),
        "slides": len(plan),
    }


def write_qa(out, plan, render_issues=None):
    qa = out / "outputs" / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    required = [
        "deck_brief.md",
        "ast_outline.md",
        "slide_plan.json",
        "speaker_intent.md",
        "asset_manifest.md",
        "video_slots.json",
        "router_plan.json",
        "run_manifest.json",
    ]
    checks = []
    for name in required:
        checks.append((name, (out / name).exists()))
    visible_text = "\n".join("\n".join(p.get("visible_content", [])) for p in plan)
    banned = [x for x in BANNED_VISIBLE_PATTERNS if x in visible_text]
    checks.append(("visible_slide_text_has_no_ai_draft_markers", not banned))
    missing = [name for name, ok in checks if not ok]
    render_issues = render_issues or []
    missing.extend(render_issues)
    report = ["# QA Report", "", f"- status: {'pass' if not missing else 'needs-fix'}", "", "## Checks"]
    report.extend([f"- [{'x' if ok else ' '}] {name}" for name, ok in checks])
    report.extend([f"- [ ] {issue}" for issue in render_issues])
    if banned:
        report.extend(["", "## Banned visible markers", *[f"- {x}" for x in banned]])
    (qa / "qa_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (qa / "fix_list.md").write_text("# Fix List\n\n" + ("No blocking issues.\n" if not missing else "\n".join(f"- Fix {x}" for x in missing) + "\n"), encoding="utf-8")
    return not missing


def write_manifest(out, title, source_path, primary, routes, qa_passed):
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    manifest = {
        "version": VERSION,
        "generated_at": now_iso(),
        "title": title,
        "source": str(source_path),
        "primary_renderer": primary,
        "routes": routes,
        "qa_status": "pass" if qa_passed else "needs-fix",
        "files": files,
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    final_dir = out / "outputs" / "qa"
    final_dir.mkdir(parents=True, exist_ok=True)
    (final_dir / "final_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_style_brief(out, primary, language, preview_count=None):
    if language == "zh":
        route_rule = "中文默认走 guizang 稳定成稿；用户显式要求时再进入 preview-first。"
    else:
        route_rule = f"英文默认先定主题，再生成至少 {preview_count or DEFAULT_EN_PREVIEW_COUNT} 个风格候选；选中风格后才进入完整 deck、presenter 和 deploy。"
    style = {
        "version": VERSION,
        "primary_renderer": primary,
        "language": language,
        "style_mode": "stable-first" if primary == "guizang" else "preview-first",
        "rule": "先保留AST叙事，再选择视觉系统；不要把推荐Skill清单写成产品边界。",
        "route_rule": route_rule,
        "preview_count": preview_count,
    }
    (out / "style_brief.md").write_text(
        "# Style Brief\n\n"
        f"- primary_renderer: `{primary}`\n"
        f"- language: `{language}`\n"
        f"- style_mode: `{style['style_mode']}`\n"
        f"- preview_count: `{preview_count}`\n"
        f"- route_rule: {route_rule}\n"
        f"- principle: {style['rule']}\n",
        encoding="utf-8",
    )
    return style


def copy_registry_snapshot(out):
    target = out / "renderer_registry.json"
    if REGISTRY_PATH.exists():
        shutil.copyfile(REGISTRY_PATH, target)


def parse_args():
    ap = argparse.ArgumentParser(
        description="Humanize PPT v0.6.4 — outline director + per-page media decision + brief orchestrator + post-render QA loop"
    )
    ap.add_argument("--source", default=None, help="Source markdown / PPTX. Required for brief mode.")
    ap.add_argument("--out", required=True, help="Output directory.")
    ap.add_argument("--title", default=None, help="Deck title. Required for brief mode.")
    ap.add_argument("--qa-from", default=None, help="Path to a rendered HTML deck. Switches to QA mode. Mutually exclusive with --source.")
    ap.add_argument("--max-qa-iterations", type=int, default=3, help="Max QA rounds before status flips to needs-human. Default 3.")
    ap.add_argument("--renderer", default="auto", choices=["auto", "guizang", "beautiful-html-templates", "html-ppt", "frontend-slides"])
    ap.add_argument("--style-mode", default="stable-first", choices=["stable-first", "preview-first", "presenter-first"])
    ap.add_argument("--selected-template", default=None, help="Beautiful template slug to render as a full deck after preview selection.")
    ap.add_argument("--presenter-adapter", action="store_true", help="Generate outputs/presenter/index.html for speaker notes and presenter control.")
    ap.add_argument("--export-adapter", action="store_true", help="Generate outputs/export package and export_pdf.sh for PDF export.")
    ap.add_argument("--occasion", default=None, help="Optional occasion hint for beautiful-html-templates selection.")
    ap.add_argument("--mood", default=None, help="Optional mood/vibe hint for beautiful-html-templates selection.")
    ap.add_argument("--preview-count", type=int, default=None, help="Number of beautiful-html-templates previews to render. English runs are floored at 5.")
    ap.add_argument("--beautiful-repo", default=None, help="Path to zarazhangrui/beautiful-html-templates. Auto-detected if omitted.")
    ap.add_argument("--no-beautiful-auto-clone", action="store_true", help="Do not auto-clone beautiful-html-templates into ~/.cache/humanize-ppt.")
    ap.add_argument("--presenter", action="store_true")
    ap.add_argument("--no-render", action="store_true", help="Only write contracts, router plan, commands, and manifest.")
    ap.add_argument("--guizang-style", default=None, choices=["A", "B"], help="Guizang style (A = flexible, B = Swiss locked). Defaults to A.")
    ap.add_argument(
        "--guizang-theme",
        default=None,
        choices=["ink-classic", "indigo-porcelain", "forest-ink", "kraft-paper", "dune"],
        help="Style A theme preset. Required when --guizang-style=A. v0.6.5: 5 built-in presets, no custom colors.",
    )
    ap.add_argument(
        "--guizang-accent",
        default=None,
        choices=["ikb", "lemon-yellow", "lemon-green", "safety-orange"],
        help="Style B accent color. Required when --guizang-style=B. v0.6.5: pick 1 of 4.",
    )
    ap.add_argument(
        "--research-md",
        default=None,
        help="Path to a pre-existing research document (e.g. hv-analysis output) to use as the brief source instead of --source.",
    )
    ap.add_argument(
        "--skip-install-check",
        action="store_true",
        help="Skip the guizang-ppt-skill (or relevant downstream skill) install self-check warning.",
    )
    return ap.parse_args()


def main():
    args = parse_args()

    if args.qa_from:
        return run_qa_mode(args)

    if not (args.title and (args.source or getattr(args, "research_md", None))):
        sys.stderr.write(
            "--title plus (--source or --research-md) are required for brief mode, "
            "or pass --qa-from for QA mode\n"
        )
        return 2

    out = Path(args.out).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # v0.6.5: if --research-md is provided, it takes priority over --source.
    # The HV research document becomes the authoritative source. The brief
    # writer does not re-parse raw material.
    if getattr(args, "research_md", None):
        research_path = Path(args.research_md).expanduser().resolve()
        if not research_path.exists():
            sys.stderr.write(f"--research-md path not found: {research_path}\n")
            return 2
        source_path, text, segments = read_source(str(research_path))
    else:
        source_path, text, segments = read_source(args.source)
    language = detect_language(text)
    preview_count = resolve_preview_count(language, args.preview_count)
    registry = load_registry()
    primary, routes = choose_routes(args, source_path, text, language)
    if primary == "beautiful-html-templates" and not args.selected_template:
        for route in routes:
            if route["id"] == "beautiful-html-templates":
                route["style_gate"] = "theme-first"
                route["preview_count"] = preview_count
    plan = build_slide_plan(args.title, text, segments, primary)

    write_contracts(out, args.title, source_path, text, plan, language)
    write_style_brief(out, primary, language, preview_count=preview_count)
    copy_registry_snapshot(out)
    router_plan = write_router_plan(out, args.title, source_path, primary, routes, registry)
    write_commands(out, router_plan)

    rendered = None
    render_issues = []
    # v0.6.4: Humanize PPT no longer imitates any downstream renderer.
    # It writes a production brief; the named skill renders natively.
    if not args.no_render:
        if primary == "guizang":
            # v0.6.5: 9 combos = Style A (5 themes) + Style B (4 accents).
            # Mutex: A requires --guizang-theme, B requires --guizang-accent.
            style = getattr(args, "guizang_style", None) or "A"
            theme = getattr(args, "guizang_theme", None)
            accent = getattr(args, "guizang_accent", None)
            if style == "A" and not theme:
                sys.stderr.write(
                    "[humanize-ppt v0.6.5] --guizang-style=A requires --guizang-theme. "
                    "Choose one of: ink-classic, indigo-porcelain, forest-ink, kraft-paper, dune. "
                    "Defaulting to ink-classic.\n"
                )
                theme = "ink-classic"
            if style == "B" and not accent:
                sys.stderr.write(
                    "[humanize-ppt v0.6.5] --guizang-style=B requires --guizang-accent. "
                    "Choose one of: ikb, lemon-yellow, lemon-green, safety-orange. "
                    "Defaulting to ikb.\n"
                )
                accent = "ikb"
            if style == "A" and accent:
                sys.stderr.write(
                    f"[humanize-ppt v0.6.5] --guizang-style=A ignores --guizang-accent={accent}.\n"
                )
            if style == "B" and theme:
                sys.stderr.write(
                    f"[humanize-ppt v0.6.5] --guizang-style=B ignores --guizang-theme={theme}.\n"
                )
            # v0.6.5: install self-check. Warn-only; the brief still ships.
            check_downstream_install(
                "guizang-ppt-skill",
                skip=getattr(args, "skip_install_check", False),
            )
            brief_result = write_guizang_production_brief(
                out,
                title=args.title,
                plan=plan,
                source=source_path,
                language=language,
                style=style,
                theme=theme,
                accent=accent,
            )
            for route in router_plan["routes"]:
                if route["id"] == "guizang":
                    route["status"] = brief_result["status"]
                    route["actual_output"] = brief_result["prompt"]
                    if style == "A":
                        route["theme"] = theme
                    else:
                        route["accent"] = accent
        elif primary == "frontend-slides":
            check_downstream_install(
                "frontend-slides",
                skip=getattr(args, "skip_install_check", False),
            )
            brief_result = write_frontend_slides_production_brief(
                out,
                title=args.title,
                plan=plan,
                source=source_path,
                language=language,
            )
            for route in router_plan["routes"]:
                if route["id"] == "frontend-slides":
                    route["status"] = brief_result["status"]
                    route["actual_output"] = brief_result["prompt"]
        elif primary == "beautiful-html-templates":
            check_downstream_install(
                "beautiful-html-templates",
                skip=getattr(args, "skip_install_check", False),
            )
            brief_result = write_beautiful_html_templates_production_brief(
                out,
                title=args.title,
                plan=plan,
                source=source_path,
                language=language,
            )
            for route in router_plan["routes"]:
                if route["id"] == "beautiful-html-templates":
                    route["status"] = brief_result["status"]
                    route["actual_output"] = brief_result["prompt"]
                    route["style_gate"] = "theme-first"
                    route["preview_count"] = preview_count

    final_deck = None  # v0.6.4: Humanize does not own a rendered deck anymore.

    if args.presenter_adapter:
        if final_deck and final_deck.exists():
            presenter_result = write_presenter_adapter(out, args.title, plan, final_deck)
        else:
            presenter_result = {"status": "missing-deck", "message": "presenter adapter requires a rendered final deck; use --selected-template or a renderer that emits outputs/<renderer>/index.html."}
            render_issues.append(f"presenter adapter: {presenter_result['status']} — {presenter_result['message']}")
        if presenter_result.get("status") != "rendered" and not any("presenter adapter:" in issue for issue in render_issues):
            render_issues.append(f"presenter adapter: {presenter_result.get('status')} — {presenter_result.get('message')}")
        for route in router_plan["routes"]:
            if route["id"] == "presenter-adapter":
                route["status"] = presenter_result.get("status")
                route["actual_output"] = presenter_result.get("presenter")
                route["manifest"] = presenter_result.get("manifest")

    if args.export_adapter:
        if final_deck and final_deck.exists():
            export_result = write_export_adapter(out, args.title, final_deck, len(plan))
        else:
            export_result = {"status": "missing-deck", "message": "export adapter requires a rendered final deck; use --selected-template or a renderer that emits outputs/<renderer>/index.html."}
            render_issues.append(f"export adapter: {export_result['status']} — {export_result['message']}")
        if export_result.get("status") != "packaged" and not any("export adapter:" in issue for issue in render_issues):
            render_issues.append(f"export adapter: {export_result.get('status')} — {export_result.get('message')}")
        for route in router_plan["routes"]:
            if route["id"] == "export-adapter":
                route["status"] = export_result.get("status")
                route["actual_output"] = export_result.get("package")
                route["manifest"] = export_result.get("manifest")

    (out / "router_plan.json").write_text(json.dumps(router_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    write_manifest(out, args.title, source_path, primary, router_plan["routes"], qa_passed=False)
    qa_passed = write_qa(out, plan, render_issues=render_issues)
    for route in router_plan["routes"]:
        if route["id"] == "qa":
            route["status"] = "pass" if qa_passed else "needs-fix"
            route["actual_output"] = str(out / "outputs" / "qa" / "qa_report.md")
    (out / "router_plan.json").write_text(json.dumps(router_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = write_manifest(out, args.title, source_path, primary, router_plan["routes"], qa_passed=qa_passed)
    print(
        json.dumps(
            {
                "ok": qa_passed,
                "version": VERSION,
                "out": str(out),
                "primary_renderer": primary,
                "router_plan": str(out / "router_plan.json"),
                "run_manifest": str(out / "run_manifest.json"),
                "rendered": str(rendered) if rendered else None,
                "qa_report": str(out / "outputs" / "qa" / "qa_report.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
