# WorkBuddy Team Agent V0.2 Implementation Plan

> Goal: keep Humanize PPT as a reusable Skill, then package it into a Tencent WorkBuddy Team Agent with role-specific agents.

## Corrected positioning

Humanize PPT is not the Team Agent itself. It remains:

```text
humanize-ppt = AST-based outline director Skill
```

The WorkBuddy product package is:

```text
humanize-ppt-team = Team Agent expert package
```

The Team Agent includes `skills/humanize-ppt/` and coordinates member agents around it.

---

## Task 1: Create WorkBuddy package skeleton

Create:

```text
workbuddy/humanize-ppt-team/
├── .workbuddy-plugin/plugin.json
├── agents/
├── avatars/
├── skills/humanize-ppt/
├── settings.json
└── README.md
```

Validation:

- `plugin.json.expertType` is `team`.
- `plugin.json.agentName` is `humanize-ppt-team-lead`.
- `settings.json.agent` is `humanize-ppt-team-lead`.
- No `hooks/`, `commands/`, `.lsp.json`.

---

## Task 2: Copy Humanize PPT as a Skill resource

Copy the current Skill files into:

```text
workbuddy/humanize-ppt-team/skills/humanize-ppt/
```

Minimum required:

```text
SKILL.md
contracts/
docs/
adapters/
scripts/
examples/
```

Do not rewrite this Skill as an Agent.

---

## Task 3: Add Team Agent members

Create:

```text
agents/humanize-ppt-team-lead.md
agents/outline-director.md
agents/renderer.md
agents/presenter.md
agents/qa.md
```

Rules:

- Frontmatter `name` equals filename without `.md`.
- Do not add `tools` in frontmatter.
- Lead file must not be generic `team-lead.md`.
- Lead prompt must include WorkBuddy team collaboration iron rules.

---

## Task 4: Make renderer Skill-agnostic

The renderer Agent should not be hard-coded to four skills.

It should follow this decision order:

1. If user names a PPT/HTML PPT Skill, adapt to that Skill.
2. If user does not name one, recommend from known good paths:
   - guizang-ppt-skill for stable Chinese decks.
   - frontend-slides / Zara path for style exploration and deploy.
   - html-ppt / presenter path for speaker mode.
   - HyperFrames path for motion/video slots.
3. If none match, output an adapter brief rather than pretending support exists.

---

## Task 5: Package and validate

Run:

```bash
cd workbuddy
zip -r humanize-ppt-team.zip humanize-ppt-team/
```

Self-check:

- All paths in `plugin.json.agents` exist.
- All paths in `plugin.json.skills` exist and contain `SKILL.md`.
- All avatar paths exist before submission.
- `members[].id` equals corresponding agent filenames.
- `teamInfo.memberAgents[]` does not include the lead.

---

## Acceptance criteria

- README and SKILL.md say Humanize PPT is a Skill.
- WorkBuddy docs say the Team Agent is a packaging/orchestration layer.
- The Team Agent can adapt to different downstream PPT/HTML PPT skills.
- Guizang/Zara/HyperFrames/Presenter are recommended examples, not fixed dependencies.
- WorkBuddy package follows the v2.1 directory and metadata rules.
