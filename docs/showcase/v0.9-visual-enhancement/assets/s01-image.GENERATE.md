# s01-image.png — pending (gpt-photo, needs OPENAI_API_KEY)

This media slot is kind `gpt-photo` (synthesized hero image). Humanize decided
*what* and *where*; producing it needs an image-generation skill with a key —
which is NOT set in this environment (`OPENAI_API_KEY` unset). Per 宁空不摆拍,
the slot is left as an executable task, not a faked PNG.

Run with your key (imagegen skill, ~/.agents/skills/imagegen):

    OPENAI_API_KEY=sk-... python3 ~/.agents/skills/imagegen/scripts/image_gen.py \
      --prompt "AI 工具更新主题的杂志感 hero 配图：暗色编辑风，抽象的工具/工作流意象，无文字，16:9" \
      --size 1536x1024 --out s01-image.png

prompt_hint (from slide_plan): cover/hook image for《AI 工具更新，不只是功能清单》.
aspect_ratio: 16:9 · honor max_size_kb from the slide_plan slot.
