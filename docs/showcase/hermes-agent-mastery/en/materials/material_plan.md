# English Neo-Grid Material Plan

This material pass should happen before presenter mode.

## Rule

Use generated media only where it adds meaning. Exact labels and system diagrams should stay deterministic SVG/HTML. GPT Image 2 should produce non-textual atmosphere or hero stills. Remotion should produce short process clips, not replace the deck.

## Slide Assignments

| slide | material | producer | output | why |
|---|---|---|---|---|
| S01 | B&W Hermes workbench atmosphere | GPT Image 2 | `materials/images/01-cover-workbench.png` | replace generic photo placeholders without risking text artifacts |
| S03 | entry loop process clip | Remotion | `materials/videos/03-entry-loop.mp4` + poster PNG | show the first reliable loop as motion |
| S04 | tools boundary diagram | deterministic SVG/HTML | `materials/diagrams/04-tools-boundary.svg` | exact labels matter; do not use image generation for text |
| S05 | skill operating card | deterministic SVG/HTML | `materials/diagrams/05-skill-operating-card.svg` | exact workflow labels and QA checks |
| S06 | context stack diagram | deterministic SVG/HTML | `materials/diagrams/06-context-stack.svg` | exact project/task/personal labels |
| S07 | agent handoff clip | Remotion | `materials/videos/07-agent-handoff.mp4` + poster PNG | make team ownership visible |
| S08 | final workbench hero still | GPT Image 2 | `materials/images/08-workbench-outcome.png` | non-textual closing visual |
| S09 | effect-test workbench still | GPT Image 2 | `materials/images/09-image2-workbench.png` | added as an extra page to judge Image 2 inside Neo-Grid |
| S10 | effect-test entry loop video | Remotion | `materials/videos/10-remotion-entry-loop.mp4` + poster PNG | added as an extra page to judge motion inside Neo-Grid |

## GPT Image 2 Prompts

### S01 Cover

Editorial black-and-white photograph style, a minimal AI agent workbench: laptop, terminal windows, notebook, printed grid cards, cables, dark desk, high contrast, modern design studio mood, no readable text, no logos, no people, 16:9.

### S08 Closing

Editorial black-and-white still life of a mature agent workbench: organized files, terminal glow, QA checklist cards, modular tools, confident product studio atmosphere, subtle neon yellow accent object, no readable text, no logos, 16:9.

## Remotion Briefs

### S03 Entry Loop

8-10 seconds, 16:9, Neo-Grid Bold style. Four blocks appear in sequence: Install, Configure, Doctor, Deliver. A small status line moves through read -> act -> check -> write back. Export MP4 and a poster PNG.

### S07 Agent Handoff

8-12 seconds, 16:9, Neo-Grid Bold style. Four panels hand off a work artifact: Design Agent -> Build Agent -> QA Agent -> Deploy Agent. Each handoff shows a visible check. Export MP4 and a poster PNG.

## Insert Policy

For the current deck, keep the core 8-slide structure. Insert stills into existing photo/panel regions or use video poster frames until presenter/deploy confirms browser playback constraints.
